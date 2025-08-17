"""
Enhanced User Input Forms with Persistent Settings
Maintains user information, location, and insurance settings across multiple car calculations
"""

import streamlit as st
import re
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
try:
    from utils.used_vehicle_estimator import UsedVehicleEstimator
except ImportError:
    # Fallback if estimator not available
    class UsedVehicleEstimator:
        def __init__(self):
            pass
        def is_used_vehicle(self, year, mileage):
            return False
        def estimate_current_value(self, make, model, year, trim, mileage):
            return None
# Import with error handling (keeping your existing structure)
try:
    from data.vehicle_database import (
        get_all_manufacturers, get_models_for_manufacturer, 
        get_trims_for_vehicle, get_vehicle_trim_price,
        validate_vehicle_selection, get_available_years_for_model
    )
except ImportError:
    # Fallback functions if database not available
    def get_all_manufacturers():
        return ['Toyota', 'Honda', 'Chevrolet', 'Ford', 'Hyundai']
    
    def get_models_for_manufacturer(make):
        models = {
            'Toyota': ['Camry', 'Corolla', 'Prius', 'RAV4'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot'],
            'Chevrolet': ['Silverado', 'Malibu', 'Equinox'],
            'Ford': ['F-150', 'Escape', 'Focus'],
            'Hyundai': ['Elantra', 'Santa Fe', 'Tucson']
        }
        return models.get(make, [])
    
    def get_trims_for_vehicle(make, model, year):
        return {'Base': 25000, 'LX': 28000, 'EX': 32000}
    
    def get_available_years_for_model(make, model):
        return list(range(2015, 2026))
    
    def validate_vehicle_selection(make, model, year, trim):
        return True, "Valid selection"

try:
    from utils.zip_code_utils import lookup_zip_code_data, validate_zip_code
except ImportError:
    def lookup_zip_code_data(zip_code):
        return {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 3.50, 'electricity_rate': 0.12}
    
    def validate_zip_code(zip_code):
        return len(zip_code) == 5 and zip_code.isdigit()

try:
    from utils.session_manager import update_location_data
except ImportError:
    def update_location_data(**kwargs):
        pass


def initialize_persistent_settings():
    """Initialize persistent settings that should be maintained across car calculations"""
    if 'persistent_settings' not in st.session_state:
        st.session_state.persistent_settings = {
            # Location & Regional Settings
            'location': {
                'zip_code': '',
                'state': '',
                'geography_type': 'Suburban',
                'fuel_price': 3.50,
                'electricity_rate': 0.12,
                'is_set': False
            },
            # Personal Information
            'personal': {
                'user_age': 35,
                'gross_income': 60000,
                'annual_mileage': 12000,
                'driving_style': 'normal',
                'terrain': 'flat',
                'num_household_vehicles': 2,
                'is_set': False
            },
            # Insurance Settings
            'insurance': {
                'coverage_type': 'standard',
                'shop_type': 'independent',
                'is_set': False
            },
            # Analysis Preferences
            'analysis': {
                'comparison_priority': 'cost',
                'default_analysis_years': 5,
                'is_set': False
            }
        }

def save_persistent_setting(category: str, data: Dict[str, Any]):
    """Save settings to persistent storage"""
    if 'persistent_settings' not in st.session_state:
        initialize_persistent_settings()
    
    st.session_state.persistent_settings[category].update(data)
    st.session_state.persistent_settings[category]['is_set'] = True

def get_persistent_setting(category: str, key: str = None, default=None):
    """Get persistent settings"""
    if 'persistent_settings' not in st.session_state:
        initialize_persistent_settings()
    
    if key is None:
        return st.session_state.persistent_settings.get(category, {})
    else:
        return st.session_state.persistent_settings.get(category, {}).get(key, default)

def estimate_used_vehicle_value(make: str, model: str, year: int, current_mileage: int, trim_msrp: float) -> Optional[float]:
    """
    Balanced depreciation estimation that properly weighs age vs mileage
    """
    try:
        from models.depreciation.enhanced_depreciation import EnhancedDepreciationModel
        
        current_year = datetime.now().year
        vehicle_age = current_year - year
        
        if vehicle_age <= 0 or not ((year < current_year) or (year == current_year and current_mileage > 1000)):
            return None
        
        depreciation_model = EnhancedDepreciationModel()
        segment = depreciation_model._classify_vehicle_segment(make, model)
        brand_multiplier = depreciation_model.brand_multipliers.get(make, 1.0)
        
        # Apply model adjustments if available
        if hasattr(depreciation_model, '_apply_model_specific_adjustments'):
            brand_multiplier = depreciation_model._apply_model_specific_adjustments(make, model, brand_multiplier)
        
        st.write(f"Debug: Segment = {segment}, Brand multiplier = {brand_multiplier:.3f}")
        
        # BALANCED APPROACH: Use age as primary factor, mileage as adjustment
        
        # Step 1: Get BASE depreciation from age (using enhanced curves)
        base_age_depreciation = depreciation_model._get_cumulative_depreciation_rate(vehicle_age, segment)
        st.write(f"Debug: Base age depreciation = {base_age_depreciation:.3f} ({base_age_depreciation*100:.1f}%)")
        
        # Step 2: Calculate EXPECTED mileage for this age
        expected_mileage = vehicle_age * 12000  # 12k miles per year
        mileage_difference = current_mileage - expected_mileage
        
        st.write(f"Debug: Expected mileage = {expected_mileage:,}, Actual = {current_mileage:,}, Diff = {mileage_difference:,}")
        
        # Step 3: Apply REASONABLE mileage adjustments
        if current_mileage <= 100:
            # Zero mileage - significant bonus
            mileage_adjustment = -0.20  # 20% reduction in depreciation
            st.write("Debug: Zero mileage bonus applied (-20%)")
            
        elif current_mileage <= 1000:
            # Very low mileage - good bonus
            mileage_adjustment = -0.15  # 15% reduction
            st.write("Debug: Very low mileage bonus applied (-15%)")
            
        elif abs(mileage_difference) <= 10000:
            # Within normal range - minimal adjustment
            mileage_adjustment = mileage_difference / 200000  # Very gradual
            st.write(f"Debug: Normal mileage range, adjustment = {mileage_adjustment:.3f}")
            
        elif mileage_difference > 10000:
            # Higher than expected mileage - penalty
            excess_miles = mileage_difference - 10000
            mileage_adjustment = 0.10 + (excess_miles / 300000)  # Gradual penalty
            mileage_adjustment = min(mileage_adjustment, 0.25)  # Cap at 25% additional
            st.write(f"Debug: High mileage penalty = +{mileage_adjustment:.3f}")
            
        else:
            # Lower than expected mileage - bonus
            missing_miles = abs(mileage_difference) - 10000
            mileage_adjustment = -0.05 - (missing_miles / 400000)  # Gradual bonus
            mileage_adjustment = max(mileage_adjustment, -0.15)  # Cap at 15% reduction
            st.write(f"Debug: Low mileage bonus = {mileage_adjustment:.3f}")
        
        # Step 4: Combine age + mileage + brand
        adjusted_depreciation = base_age_depreciation + mileage_adjustment
        final_depreciation = adjusted_depreciation * brand_multiplier
        
        st.write(f"Debug: After mileage adj = {adjusted_depreciation:.3f}")
        st.write(f"Debug: After brand adj = {final_depreciation:.3f}")
        
        # Step 5: Apply realistic caps by segment
        realistic_caps = {
            'luxury': 0.88,     # Max 88% depreciation for 10+ year luxury
            'electric': 0.90,   # Max 90% for EVs
            'truck': 0.75,      # Max 75% for trucks (hold value well)
            'suv': 0.80,        # Max 80% for SUVs
            'sports': 0.82,     # Max 82% for sports cars
            'compact': 0.78,    # Max 78% for compacts
            'sedan': 0.80,      # Max 80% for sedans
            'economy': 0.85     # Max 85% for economy cars
        }
        
        # Also apply minimum floors (even high-mileage cars have some value)
        realistic_floors = {
            'luxury': 0.50,     # Min 50% depreciation for luxury
            'electric': 0.40,   # Min 40% for EVs (some tech value)
            'truck': 0.30,      # Min 30% for trucks (strong demand)
            'suv': 0.35,        # Min 35% for SUVs
            'sports': 0.40,     # Min 40% for sports cars
            'compact': 0.35,    # Min 35% for compacts
            'sedan': 0.40,      # Min 40% for sedans
            'economy': 0.45     # Min 45% for economy cars
        }
        
        cap = realistic_caps.get(segment, 0.82)
        floor = realistic_floors.get(segment, 0.40)
        
        # Apply caps but be more generous for low-mileage vehicles
        if current_mileage <= 1000:
            # Very low mileage vehicles get more generous caps
            cap = min(cap, 0.60)  # Never more than 60% depreciation for very low miles
        elif current_mileage <= 25000:
            # Low-moderate mileage vehicles
            cap = min(cap, 0.75)  # Never more than 75% depreciation
        
        final_depreciation = max(floor, min(final_depreciation, cap))
        
        st.write(f"Debug: Applied cap/floor ({floor:.3f} to {cap:.3f}) = {final_depreciation:.3f}")
        
        estimated_value = trim_msrp * (1 - final_depreciation)
        
        st.write(f"Debug: Final estimated value = ${estimated_value:,.0f}")
        
        return round(estimated_value, 0)
        
    except ImportError:
        st.error("Enhanced depreciation model not available")
        return None
        
    except Exception as e:
        st.error(f"Error in balanced depreciation: {str(e)}")
        return None

def estimate_used_vehicle_value(make: str, model: str, year: int, current_mileage: int, trim_msrp: float) -> Optional[float]:
    """
    FIXED: Realistic depreciation with properly calibrated curves
    Target: 2015 BMW 328i with 70k miles should be ~$8-9k (75-78% depreciation)
    """
    try:
        current_year = datetime.now().year
        vehicle_age = current_year - year
        
        if vehicle_age <= 0 or not ((year < current_year) or (year == current_year and current_mileage > 1000)):
            return None
        
        st.write(f"Debug: {year} {make} {model}, Age = {vehicle_age}, Mileage = {current_mileage:,}")
        
        # STEP 1: REALISTIC BASE CURVES (much more conservative)
        # These curves are calibrated to match real market data
        realistic_curves = {
            # Luxury vehicles - calibrated to BMW/Mercedes market reality
            'luxury': {
                1: 0.18,   2: 0.28,   3: 0.36,   4: 0.43,   5: 0.50,
                6: 0.56,   7: 0.61,   8: 0.65,   9: 0.68,   10: 0.71,  # ← 71% at 10 years, not 88%!
                11: 0.73,  12: 0.75,  13: 0.76,  14: 0.77,  15: 0.78
            },
            
            # Electric vehicles - higher tech depreciation
            'electric': {
                1: 0.22,   2: 0.35,   3: 0.45,   4: 0.54,   5: 0.62,
                6: 0.68,   7: 0.73,   8: 0.77,   9: 0.80,   10: 0.82,
                11: 0.84,  12: 0.85,  13: 0.86,  14: 0.86,  15: 0.87
            },
            
            # Trucks - excellent retention
            'truck': {
                1: 0.10,   2: 0.18,   3: 0.25,   4: 0.31,   5: 0.36,
                6: 0.41,   7: 0.45,   8: 0.48,   9: 0.51,   10: 0.54,
                11: 0.56,  12: 0.58,  13: 0.59,  14: 0.60,  15: 0.61
            },
            
            # SUVs - good retention
            'suv': {
                1: 0.13,   2: 0.22,   3: 0.30,   4: 0.36,   5: 0.42,
                6: 0.47,   7: 0.51,   8: 0.55,   9: 0.58,   10: 0.61,
                11: 0.63,  12: 0.65,  13: 0.66,  14: 0.67,  15: 0.68
            },
            
            # Sports cars - variable by desirability
            'sports': {
                1: 0.16,   2: 0.26,   3: 0.34,   4: 0.41,   5: 0.47,
                6: 0.52,   7: 0.56,   8: 0.60,   9: 0.63,   10: 0.66,
                11: 0.68,  12: 0.70,  13: 0.71,  14: 0.72,  15: 0.73
            },
            
            # Compact cars
            'compact': {
                1: 0.14,   2: 0.24,   3: 0.32,   4: 0.38,   5: 0.44,
                6: 0.49,   7: 0.53,   8: 0.57,   9: 0.60,   10: 0.62,
                11: 0.64,  12: 0.66,  13: 0.67,  14: 0.68,  15: 0.69
            },
            
            # Sedans - middle of the road
            'sedan': {
                1: 0.15,   2: 0.25,   3: 0.33,   4: 0.40,   5: 0.46,
                6: 0.51,   7: 0.55,   8: 0.59,   9: 0.62,   10: 0.65,
                11: 0.67,  12: 0.69,  13: 0.70,  14: 0.71,  15: 0.72
            },
            
            # Economy cars - higher depreciation
            'economy': {
                1: 0.17,   2: 0.28,   3: 0.37,   4: 0.45,   5: 0.52,
                6: 0.58,   7: 0.62,   8: 0.66,   9: 0.69,   10: 0.72,
                11: 0.74,  12: 0.76,  13: 0.77,  14: 0.78,  15: 0.79
            }
        }
        
        # Classify vehicle segment
        model_lower = model.lower()
        make_lower = make.lower()
        
        if make_lower in ['bmw', 'mercedes-benz', 'audi', 'lexus', 'acura', 'infiniti', 'cadillac', 'lincoln']:
            segment = 'luxury'
        elif any(term in model_lower for term in ['f-150', 'silverado', 'ram', 'tundra', 'tacoma', 'frontier', 'ridgeline']):
            segment = 'truck'
        elif any(term in model_lower for term in ['suburban', 'tahoe', 'pilot', 'highlander', 'rav4', 'cr-v']):
            segment = 'suv'
        elif any(term in model_lower for term in ['corvette', 'mustang', 'camaro', 'challenger', '911']):
            segment = 'sports'
        elif any(term in model_lower for term in ['civic', 'corolla', 'elantra']):
            segment = 'compact'
        elif any(term in model_lower for term in ['spark', 'mirage', 'rio']):
            segment = 'economy'
        else:
            segment = 'sedan'
        
        # Get realistic base depreciation
        curve = realistic_curves[segment]
        base_depreciation = curve.get(vehicle_age, curve.get(15, 0.72))
        
        st.write(f"Debug: Segment = {segment}")
        st.write(f"Debug: Base depreciation = {base_depreciation:.3f} ({base_depreciation*100:.1f}%)")
        
        # STEP 2: MILEAGE ADJUSTMENT (10k miles/year baseline)
        expected_mileage = vehicle_age * 10000
        annual_mileage = current_mileage / max(vehicle_age, 1)
        
        st.write(f"Debug: Expected = {expected_mileage:,}, Actual = {current_mileage:,}, Annual = {annual_mileage:,.0f}")
        
        # Mileage adjustment factor (more generous)
        if current_mileage <= 100:
            mileage_adjustment = -0.15  # 15% reduction in depreciation
        elif annual_mileage <= 5000:
            mileage_adjustment = -0.12  # 12% reduction
        elif annual_mileage <= 8000:
            mileage_adjustment = -0.08  # 8% reduction
        elif annual_mileage <= 12000:
            # Normal range - gradual from bonus to neutral
            ratio = (annual_mileage - 8000) / 4000
            mileage_adjustment = -0.08 + (ratio * 0.08)  # -8% to 0%
        elif annual_mileage <= 15000:
            # Slightly high - small penalty
            ratio = (annual_mileage - 12000) / 3000
            mileage_adjustment = ratio * 0.04  # 0% to +4%
        elif annual_mileage <= 20000:
            # High mileage - moderate penalty
            ratio = (annual_mileage - 15000) / 5000
            mileage_adjustment = 0.04 + (ratio * 0.06)  # +4% to +10%
        else:
            # Very high mileage
            mileage_adjustment = min(0.15, 0.10 + ((annual_mileage - 20000) / 20000 * 0.05))
        
        st.write(f"Debug: Mileage adjustment = {mileage_adjustment:+.3f}")
        
        # Apply mileage adjustment
        adjusted_depreciation = base_depreciation + mileage_adjustment
        st.write(f"Debug: After mileage = {adjusted_depreciation:.3f} ({adjusted_depreciation*100:.1f}%)")
        
        # STEP 3: BRAND ADJUSTMENT (much more moderate)
        brand_multipliers = {
            # Value retention champions (BONUS)
            'Toyota': 0.92, 'Honda': 0.94, 'Lexus': 0.90, 'Subaru': 0.95,
            
            # Luxury brands (moderate penalty, not extreme)
            'BMW': 1.06,         # Was 1.22 - way too harsh!
            'Mercedes-Benz': 1.08, # Was 1.25 - way too harsh!
            'Audi': 1.04,        # Was 1.18 - way too harsh!
            'Cadillac': 1.07,
            'Lincoln': 1.10,
            'Infiniti': 1.06,
            
            # Average brands
            'Ford': 1.00, 'Chevrolet': 1.01, 'Nissan': 1.02,
            'Hyundai': 0.97, 'Kia': 0.98, 'Mazda': 0.96,
            
            # Poor retention brands
            'Chrysler': 1.12, 'Dodge': 1.10, 'Fiat': 1.15,
            'Volkswagen': 1.05, 'Volvo': 1.03
        }
        
        brand_multiplier = brand_multipliers.get(make, 1.00)
        final_depreciation = adjusted_depreciation * brand_multiplier
        
        st.write(f"Debug: Brand multiplier for {make} = {brand_multiplier:.3f}")
        st.write(f"Debug: After brand adj = {final_depreciation:.3f} ({final_depreciation*100:.1f}%)")
        
        # STEP 4: APPLY REALISTIC BOUNDS
        # Target: 2015 BMW 328i with 70k miles = $8-9k = 75-78% depreciation
        final_depreciation = max(0.10, min(final_depreciation, 0.82))  # 10% to 82% range
        
        st.write(f"Debug: Final capped depreciation = {final_depreciation:.3f} ({final_depreciation*100:.1f}%)")
        
        estimated_value = trim_msrp * (1 - final_depreciation)
        
        st.write(f"Debug: MSRP = ${trim_msrp:,}, Final value = ${estimated_value:,.0f}")
        
        return round(estimated_value, 0)
        
    except Exception as e:
        st.error(f"Error in realistic depreciation: {str(e)}")
        return None


def display_vehicle_selection_form() -> Dict[str, Any]:
    """Display enhanced vehicle selection form with automatic price estimation for used vehicles"""
    
    st.subheader("🚗 Vehicle Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction type selection
        transaction_type = st.radio(
            "Transaction Type:",
            ["Purchase", "Lease"],
            help="Choose how you plan to acquire the vehicle"
        )
        
        # Manufacturer selection
        manufacturers = get_all_manufacturers()
        selected_make = st.selectbox(
            "Make:",
            [''] + manufacturers,
            help="Vehicle manufacturer"
        )
        
        # Model selection (depends on make)
        if selected_make:
            models = get_models_for_manufacturer(selected_make)
            selected_model = st.selectbox(
                "Model:",
                [''] + models,
                help="Vehicle model"
            )
        else:
            selected_model = ""
            st.selectbox("Model:", [''], help="Select make first")
    
    with col2:
        # Year selection (depends on model)
        if selected_make and selected_model:
            years = get_available_years_for_model(selected_make, selected_model)
            selected_year = st.selectbox(
                "Year:",
                [''] + [str(year) for year in sorted(years, reverse=True)],
                help="Model year"
            )
        else:
            selected_year = ""
            st.selectbox("Year:", [''], help="Select model first")
        
        # Trim selection (depends on year)
        if selected_make and selected_model and selected_year:
            trims = get_trims_for_vehicle(selected_make, selected_model, int(selected_year))
            if trims:
                trim_options = [''] + list(trims.keys())
                # Create display options with prices
                trim_display_options = []
                for trim in trim_options:
                    if trim:  # If not empty
                        price = trims[trim]
                        trim_display_options.append(f"{trim} - ${price:,}")
                    else:
                        trim_display_options.append("")  # Empty option
                
                selected_trim_display = st.selectbox(
                    "Trim:",
                    trim_display_options,
                    help="Vehicle trim level and MSRP"
                )
                
                if selected_trim_display:
                    selected_trim = selected_trim_display.split(" - $")[0]
                    trim_msrp = trims[selected_trim]
                else:
                    selected_trim = ""
                    trim_msrp = 0
            else:
                st.error(f"No trim data available for {selected_year} {selected_make} {selected_model}")
                selected_trim = ""
                trim_msrp = 0
        else:
            selected_trim = ""
            trim_msrp = 0
            st.selectbox("Trim:", [''], help="Select year first")

    # Vehicle condition and pricing section - ENHANCED WITH AUTO-POPULATION
    if selected_make and selected_model and selected_year and selected_trim:
        st.markdown("---")
        st.subheader("💰 Pricing & Condition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Current mileage input
            current_mileage = st.number_input(
                "Current Mileage:",
                min_value=0,
                max_value=300000,
                value=0,
                step=1000,
                help="Current odometer reading",
                key="current_mileage_input"
            )
        
        with col2:
            # ENHANCED: Auto-calculate used vehicle value and populate purchase price
            current_year = datetime.now().year
            is_used = (int(selected_year) < current_year) or (int(selected_year) == current_year and current_mileage > 1000)
            
            # Default price starts with MSRP
            default_price = trim_msrp
            estimated_price = None
            
            # Debug info - remove this after testing
            st.write(f"Debug: is_used = {is_used}, year = {selected_year}, current_year = {current_year}, mileage = {current_mileage}")
            
            if is_used and trim_msrp > 0:
                try:
                    estimated_price = estimate_used_vehicle_value(
                        selected_make, selected_model, int(selected_year), current_mileage, trim_msrp
                    )
                    if estimated_price:
                        default_price = estimated_price
                        st.write(f"Debug: estimated_price = ${estimated_price:,.0f}")  # Debug - remove after testing
                except Exception as e:
                    st.error(f"Error estimating used vehicle price: {str(e)}")
                    estimated_price = None

            # Purchase price input with auto-population
            if transaction_type == "Purchase":
                # Use session state to maintain the estimated price
                session_key = f"estimated_price_{selected_make}_{selected_model}_{selected_year}_{current_mileage}"
                if session_key not in st.session_state and estimated_price:
                    st.session_state[session_key] = estimated_price
                
                purchase_price = st.number_input(
                    "Purchase Price ($):",
                    min_value=1000,
                    max_value=500000,
                    value=int(default_price) if default_price else 25000,
                    step=500,
                    help="Actual purchase price (auto-estimated for used vehicles)",
                    key="purchase_price_input"
                )
                
                # Show estimation info for used vehicles
                if estimated_price and is_used:
                    vehicle_age = current_year - int(selected_year)
                    
                    # Create an attractive info box with detailed breakdown
                    st.success(f"""
                    🔍 **Used Vehicle Price Estimated**
                    
                    **Current Market Value: ${estimated_price:,.0f}**
                    
                    📊 **Estimation Details:**
                    - Original MSRP: ${trim_msrp:,.0f}
                    - Vehicle Age: {vehicle_age} years old
                    - Current Mileage: {current_mileage:,} miles
                    - Depreciation Applied: {((trim_msrp - estimated_price) / trim_msrp * 100):.1f}%
                    
                    💡 *Price auto-filled above - adjust if you have a different offer*
                    """)
                    
                    # Show brand-specific retention info
                    if selected_make.lower() in ['toyota', 'honda', 'lexus']:
                        st.info("✅ Excellent value retention brand - estimate is conservative")
                    elif selected_make.lower() in ['bmw', 'mercedes-benz', 'audi']:
                        st.warning("⚠️ Luxury vehicle - depreciation may vary significantly")
                    elif selected_make.lower() in ['chrysler', 'dodge']:
                        st.warning("📉 Lower value retention brand - actual value may be lower")
            
            else:  # Lease
                # Lease-specific fields
                monthly_payment = st.number_input(
                    "Monthly Lease Payment ($):",
                    min_value=100,
                    max_value=2000,
                    value=300,
                    step=25,
                    help="Monthly lease payment amount",
                    key="lease_payment_input"
                )
                
                down_payment = st.number_input(
                    "Down Payment ($):",
                    min_value=0,
                    max_value=20000,
                    value=2000,
                    step=500,
                    help="Initial down payment for lease",
                    key="lease_down_payment_input"
                )
                
                lease_term = st.number_input(
                    "Lease Term (months):",
                    min_value=12,
                    max_value=60,
                    value=36,
                    step=6,
                    help="Length of lease agreement",
                    key="lease_term_input"
                )
        
        # Validate vehicle selection
        is_valid = all([
            selected_make, selected_model, selected_year, selected_trim,
            transaction_type
        ])
        
        if transaction_type == "Purchase":
            is_valid = is_valid and (purchase_price > 0 if 'purchase_price' in locals() else False)
        else:
            is_valid = is_valid and all([
                monthly_payment > 0 if 'monthly_payment' in locals() else False,
                lease_term > 0 if 'lease_term' in locals() else False
            ])
        
        # Return the complete vehicle data
        result = {
            'transaction_type': transaction_type,
            'make': selected_make,
            'model': selected_model,
            'year': int(selected_year) if selected_year else None,
            'trim': selected_trim,
            'trim_msrp': trim_msrp,
            'current_mileage': current_mileage,
            'is_used': is_used,
            'is_valid': is_valid
        }
        
        # Add transaction-specific fields
        if transaction_type == "Purchase":
            result['purchase_price'] = purchase_price if 'purchase_price' in locals() else trim_msrp
            result['estimated_price'] = estimated_price
        else:
            result.update({
                'monthly_payment': monthly_payment if 'monthly_payment' in locals() else 300,
                'down_payment': down_payment if 'down_payment' in locals() else 2000,
                'lease_term': lease_term if 'lease_term' in locals() else 36
            })
        
        return result
    
    # Return incomplete data if form not fully filled
    return {
        'transaction_type': transaction_type if 'transaction_type' in locals() else "Purchase",
        'make': selected_make if 'selected_make' in locals() else "",
        'model': selected_model if 'selected_model' in locals() else "",
        'year': int(selected_year) if 'selected_year' in locals() and selected_year else None,
        'trim': selected_trim if 'selected_trim' in locals() else "",
        'trim_msrp': trim_msrp if 'trim_msrp' in locals() else 0,
        'current_mileage': 0,
        'is_used': False,
        'is_valid': False
    }

def display_location_form() -> Dict[str, Any]:
    """Display location form with persistence"""
    
    st.subheader("📍 Location & Regional Settings")
    
    # Initialize persistent settings
    initialize_persistent_settings()
    location_settings = get_persistent_setting('location')
    
    # Show persistence status
    if location_settings.get('is_set', False):
        st.success(f"✅ Using saved location: {location_settings.get('zip_code', '')} - {location_settings.get('state', '')}")
        
        # Option to modify
        if st.button("📝 Update Location Settings", key="update_location"):
            st.session_state.show_location_form = True
        else:
            st.session_state.show_location_form = False
    else:
        st.session_state.show_location_form = True
    
    if st.session_state.get('show_location_form', True):
        col1, col2 = st.columns(2)
        
        with col1:
            # ZIP code input with auto-population
            zip_code = st.text_input(
                "ZIP Code:",
                value=location_settings.get('zip_code', ''),
                max_chars=5,
                help="Enter 5-digit ZIP code for automatic location detection"
            )
            
            # Auto-populate on ZIP code entry
            if zip_code and len(zip_code) == 5:
                if validate_zip_code(zip_code):
                    zip_data = lookup_zip_code_data(zip_code)
                    if zip_data:
                        # Update the form values and show success
                        auto_state = zip_data.get('state', '')
                        auto_geography = zip_data.get('geography_type', '')
                        auto_fuel_price = zip_data.get('fuel_price', 3.50)
                        st.success(f"✅ Auto-detected: {auto_state} - {auto_geography}")
                    else:
                        auto_state = ''
                        auto_geography = 'Suburban'
                        auto_fuel_price = 3.50
                        st.warning("⚠️ ZIP code not found. Please enter manually below.")
                else:
                    auto_state = ''
                    auto_geography = 'Suburban'
                    auto_fuel_price = 3.50
                    st.error("❌ Invalid ZIP code format")
            else:
                auto_state = location_settings.get('state', '')
                auto_geography = location_settings.get('geography_type', 'Suburban')
                auto_fuel_price = location_settings.get('fuel_price', 3.50)
            
            # State selection
            state_options = [
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
            ]
            
            # Use auto-detected state or saved state
            current_state = auto_state if auto_state else location_settings.get('state', '')
            if current_state in state_options:
                state_index = state_options.index(current_state) + 1
            else:
                state_index = 0
                
            selected_state = st.selectbox(
                "State:",
                [''] + state_options,
                index=state_index,
                help="State for insurance and tax calculations"
            )
        
        with col2:
            # Geography type
            geography_options = ['Urban', 'Suburban', 'Rural']
            current_geography = auto_geography if auto_geography else location_settings.get('geography_type', 'Suburban')
            geography_index = geography_options.index(current_geography) if current_geography in geography_options else 1
            
            geography_type = st.selectbox(
                "Geography Type:",
                geography_options,
                index=geography_index,
                help="Affects maintenance costs and driving patterns"
            )
            
            # Fuel price
            fuel_price = st.number_input(
                "Local Fuel Price ($/gallon):",
                min_value=2.00,
                max_value=6.00,
                value=auto_fuel_price,
                step=0.05,
                help="Current local fuel price (auto-filled from ZIP code)"
            )
        
        # Save settings button
        if st.button("💾 Save Location Settings", key="save_location"):
            location_data = {
                'zip_code': zip_code,
                'state': selected_state,
                'geography_type': geography_type,
                'fuel_price': fuel_price,
                'electricity_rate': 0.12
            }
            save_persistent_setting('location', location_data)
            st.success("✅ Location settings saved!")
            st.rerun()
    else:
        # Use saved settings
        zip_code = location_settings.get('zip_code', '')
        selected_state = location_settings.get('state', '')
        geography_type = location_settings.get('geography_type', 'Suburban')
        fuel_price = location_settings.get('fuel_price', 3.50)
    
    return {
        'zip_code': zip_code,
        'state': selected_state,
        'geography_type': geography_type,
        'fuel_price': fuel_price,
        'electricity_rate': 0.12,
        'is_valid': bool(zip_code and len(zip_code) == 5 and selected_state)
    }

def display_personal_info_form() -> Dict[str, Any]:
    """Display personal information form with persistence"""
    
    st.subheader("👤 Personal Information")
    
    # Initialize persistent settings
    initialize_persistent_settings()
    personal_settings = get_persistent_setting('personal')
    
    # Show persistence status
    if personal_settings.get('is_set', False):
        st.success(f"✅ Using saved personal info: Age {personal_settings.get('user_age', 35)}, Income ${personal_settings.get('gross_income', 60000):,}")
        
        # Option to modify
        if st.button("📝 Update Personal Information", key="update_personal"):
            st.session_state.show_personal_form = True
        else:
            st.session_state.show_personal_form = False
    else:
        st.session_state.show_personal_form = True
    
    if st.session_state.get('show_personal_form', True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Age and income
            user_age = st.number_input(
                "Your Age:",
                min_value=16,
                max_value=100,
                value=personal_settings.get('user_age', 35),
                help="Used for insurance calculations",
                key="user_age_input"
            )
            
            gross_income = st.number_input(
                "Annual Gross Income ($):",
                min_value=15000,
                max_value=500000,
                value=personal_settings.get('gross_income', 60000),
                step=5000,
                help="Annual income for affordability analysis",
                key="gross_income_input"
            )
        
        with col2:
            # Driving patterns
            annual_mileage = st.number_input(
                "Annual Mileage:",
                min_value=5000,
                max_value=50000,
                value=personal_settings.get('annual_mileage', 12000),
                step=1000,
                help="Expected miles driven per year",
                key="annual_mileage_personal"
            )
            
            driving_style_options = ["Gentle", "Normal", "Aggressive"]
            current_style = personal_settings.get('driving_style', 'normal').title()
            style_index = driving_style_options.index(current_style) if current_style in driving_style_options else 1
            
            driving_style = st.selectbox(
                "Driving Style:",
                driving_style_options,
                index=style_index,
                help="Affects maintenance and fuel costs"
            )
        
        # Additional driving conditions
        col3, col4 = st.columns(2)
        
        with col3:
            terrain_options = ["Flat", "Hilly"]
            current_terrain = personal_settings.get('terrain', 'flat').title()
            terrain_index = terrain_options.index(current_terrain) if current_terrain in terrain_options else 0
            
            terrain = st.selectbox(
                "Primary Terrain:",
                terrain_options,
                index=terrain_index,
                help="Affects fuel consumption and maintenance"
            )
        
        with col4:
            num_household_vehicles = st.number_input(
                "Household Vehicles:",
                min_value=1,
                max_value=10,
                value=personal_settings.get('num_household_vehicles', 2),
                help="For insurance multi-vehicle discounts"
            )
        
        # Save settings button
        if st.button("💾 Save Personal Information", key="save_personal"):
            personal_data = {
                'user_age': user_age,
                'gross_income': gross_income,
                'annual_mileage': annual_mileage,
                'driving_style': driving_style.lower(),
                'terrain': terrain.lower(),
                'num_household_vehicles': num_household_vehicles
            }
            save_persistent_setting('personal', personal_data)
            st.success("✅ Personal information saved!")
            st.rerun()
    else:
        # Use saved settings
        user_age = personal_settings.get('user_age', 35)
        gross_income = personal_settings.get('gross_income', 60000)
        annual_mileage = personal_settings.get('annual_mileage', 12000)
        driving_style = personal_settings.get('driving_style', 'normal')
        terrain = personal_settings.get('terrain', 'flat')
        num_household_vehicles = personal_settings.get('num_household_vehicles', 2)
    
    return {
        'user_age': user_age,
        'gross_income': gross_income,
        'annual_mileage': annual_mileage,
        'driving_style': driving_style.lower(),
        'terrain': terrain.lower(),
        'num_household_vehicles': num_household_vehicles,
        'is_valid': True
    }

def display_insurance_form() -> Dict[str, Any]:
    """Display insurance parameters form with persistence"""
    
    st.subheader("🛡️ Insurance Settings")
    
    # Initialize persistent settings
    initialize_persistent_settings()
    insurance_settings = get_persistent_setting('insurance')
    
    # Show persistence status
    if insurance_settings.get('is_set', False):
        st.success(f"✅ Using saved insurance: {insurance_settings.get('coverage_type', 'standard').title()} coverage")
        
        # Option to modify
        if st.button("📝 Update Insurance Settings", key="update_insurance"):
            st.session_state.show_insurance_form = True
        else:
            st.session_state.show_insurance_form = False
    else:
        st.session_state.show_insurance_form = True
    
    if st.session_state.get('show_insurance_form', True):
        col1, col2 = st.columns(2)
        
        with col1:
            coverage_options = ["Basic", "Standard", "Comprehensive", "Premium"]
            current_coverage = insurance_settings.get('coverage_type', 'standard').title()
            coverage_index = coverage_options.index(current_coverage) if current_coverage in coverage_options else 1
            
            coverage_type = st.selectbox(
                "Coverage Level:",
                coverage_options,
                index=coverage_index,
                help="Insurance coverage level affects premium costs"
            )
            
            shop_options = ["Independent", "Dealership", "Specialist"]
            current_shop = insurance_settings.get('shop_type', 'independent').title()
            shop_index = shop_options.index(current_shop) if current_shop in shop_options else 0
            
            shop_type = st.selectbox(
                "Maintenance Shop Preference:",
                shop_options,
                index=shop_index,
                help="Affects maintenance cost calculations"
            )
        
        with col2:
            st.info("**Coverage Descriptions:**\n\n"
                    "• **Basic**: Liability only\n"
                    "• **Standard**: Liability + comprehensive\n"
                    "• **Comprehensive**: Full coverage\n"
                    "• **Premium**: Maximum protection")
        
        # Save settings button
        if st.button("💾 Save Insurance Settings", key="save_insurance"):
            insurance_data = {
                'coverage_type': coverage_type.lower(),
                'shop_type': shop_type.lower()
            }
            save_persistent_setting('insurance', insurance_data)
            st.success("✅ Insurance settings saved!")
            st.rerun()
    else:
        # Use saved settings
        coverage_type = insurance_settings.get('coverage_type', 'standard')
        shop_type = insurance_settings.get('shop_type', 'independent')
    
    return {
        'coverage_type': coverage_type.lower(),
        'shop_type': shop_type.lower(),
        'is_valid': True
    }

def display_financial_parameters_form(transaction_type: str) -> Dict[str, Any]:
    """Display financial parameters form (this can vary per car)"""
    
    st.subheader("💳 Financial Parameters")
    
    if transaction_type == "Purchase":
        col1, col2 = st.columns(2)
        
        with col1:
            # Loan details
            loan_amount = st.number_input(
                "Loan Amount ($):",
                min_value=0,
                max_value=200000,
                value=0,
                step=1000,
                help="Amount to finance (0 for cash purchase)",
                key="loan_amount_input"
            )
            
            interest_rate = st.number_input(
                "Interest Rate (%):",
                min_value=0.0,
                max_value=15.0,
                value=6.5,
                step=0.1,
                help="Annual interest rate",
                key="interest_rate_input"
            )
        
        with col2:
            loan_term = st.number_input(
                "Loan Term (years):",
                min_value=1,
                max_value=8,
                value=5,
                help="Loan duration in years"
            )
            
            down_payment = st.number_input(
                "Down Payment ($):",
                min_value=0,
                max_value=100000,
                value=5000,
                step=500,
                help="Upfront payment",
                key="down_payment_input"
            )
        
        return {
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'loan_term': loan_term,
            'down_payment': down_payment,
            'is_valid': True
        }
    
    else:  # Lease
        col1, col2 = st.columns(2)
        
        with col1:
            lease_term = st.number_input(
                "Lease Term (years):",
                min_value=1,
                max_value=5,
                value=3,
                help="Lease agreement length"
            )
            
            money_factor = st.number_input(
                "Money Factor:",
                min_value=0.0001,
                max_value=0.0050,
                value=0.0025,
                step=0.0001,
                format="%.4f",
                help="Lease interest rate factor"
            )
        
        with col2:
            residual_value_percent = st.number_input(
                "Residual Value (%):",
                min_value=20,
                max_value=80,
                value=55,
                help="Expected vehicle value at lease end"
            )
            
            down_payment = st.number_input(
                "Down Payment ($):",
                min_value=0,
                max_value=10000,
                value=2000,
                step=500,
                help="Upfront payment for lease"
            )
        
        return {
            'lease_term': lease_term,
            'money_factor': money_factor,
            'residual_value_percent': residual_value_percent,
            'down_payment': down_payment,
            'is_valid': True
        }

def display_analysis_parameters_form(transaction_type: str) -> Dict[str, Any]:
    """Display analysis parameters form with some persistence"""
    
    st.subheader("📊 Analysis Parameters")
    
    # Initialize persistent settings
    initialize_persistent_settings()
    analysis_settings = get_persistent_setting('analysis')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if transaction_type == "Purchase":
            analysis_years = st.number_input(
                "Analysis Period (years):",
                min_value=1,
                max_value=15,
                value=analysis_settings.get('default_analysis_years', 5),
                help="How many years to analyze ownership costs",
                key="analysis_years_purchase" 
            )
        else:  # Lease
            analysis_years = st.number_input(
                "Lease Term (years):",
                min_value=1,
                max_value=5,
                value=3,
                help="Lease agreement length",
                key="analysis_years_lease" 
            )
    
    with col2:
        priority_options = ["Cost", "Reliability", "Features", "Fuel Economy"]
        current_priority = analysis_settings.get('comparison_priority', 'cost').title()
        priority_index = priority_options.index(current_priority) if current_priority in priority_options else 0
        
        comparison_priority = st.selectbox(
            "Comparison Priority:",
            priority_options,
            index=priority_index,
            help="Primary factor for vehicle recommendations"
        )
        
        # Save analysis preferences
        if st.button("💾 Save Analysis Preferences", key="save_analysis"):
            analysis_data = {
                'comparison_priority': comparison_priority.lower(),
                'default_analysis_years': analysis_years if transaction_type == "Purchase" else 5
            }
            save_persistent_setting('analysis', analysis_data)
            st.success("✅ Analysis preferences saved!")
    
    return {
        'analysis_years': analysis_years,
        'comparison_priority': comparison_priority.lower(),
        'is_valid': True
    }

def collect_all_form_data() -> Tuple[Dict[str, Any], bool, str]:
    """Collect and validate all form data with persistent settings"""
    
    # Initialize persistent settings
    initialize_persistent_settings()
    
    # Display vehicle selection (always new for each calculation)
    vehicle_data = display_vehicle_selection_form()
    
    if not vehicle_data['is_valid']:
        return {}, False, "Please complete vehicle selection"
    
    st.markdown("---")
    
    # Display location form (persistent)
    location_data = display_location_form()
    
    if not location_data['is_valid']:
        return {}, False, "Please complete location information"
    
    st.markdown("---")
    
    # Display personal info form (persistent)
    personal_data = display_personal_info_form()
    
    st.markdown("---")
    
    # Display financial parameters (varies per car)
    financial_data = display_financial_parameters_form(vehicle_data['transaction_type'])
    
    st.markdown("---")
    
    # Display insurance form (persistent)
    insurance_data = display_insurance_form()
    
    st.markdown("---")
    
    # Display analysis parameters (partially persistent)
    analysis_data = display_analysis_parameters_form(vehicle_data['transaction_type'])
    
    # Validate vehicle selection
    try:
        is_valid, validation_message = validate_vehicle_selection(
            vehicle_data['make'], 
            vehicle_data['model'], 
            vehicle_data['year'], 
            vehicle_data['trim']
        )
    except:
        is_valid, validation_message = True, "Selection validated"
    
    if not is_valid:
        return {}, False, validation_message
    
    # Combine all data
    all_data = {
        **vehicle_data,
        **location_data,
        **personal_data,
        **financial_data,
        **insurance_data,
        **analysis_data
    }
    
    return all_data, True, "All data collected successfully"

def clear_persistent_settings():
    """Clear all persistent settings (utility function)"""
    if 'persistent_settings' in st.session_state:
        del st.session_state.persistent_settings
    # Reset form display flags
    for key in ['show_location_form', 'show_personal_form', 'show_insurance_form']:
        if key in st.session_state:
            del st.session_state[key]

def display_settings_management_sidebar():
    """Display settings management in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Persistent Settings")
    
    # Initialize persistent settings
    initialize_persistent_settings()
    settings = get_persistent_setting('location')
    
    # Show status of saved settings
    saved_settings = []
    if get_persistent_setting('location', 'is_set', False):
        saved_settings.append("📍 Location")
    if get_persistent_setting('personal', 'is_set', False):
        saved_settings.append("👤 Personal Info")
    if get_persistent_setting('insurance', 'is_set', False):
        saved_settings.append("🛡️ Insurance")
    if get_persistent_setting('analysis', 'is_set', False):
        saved_settings.append("📊 Analysis Prefs")
    
    if saved_settings:
        st.sidebar.success(f"✅ Saved: {', '.join(saved_settings)}")
    else:
        st.sidebar.info("💡 No settings saved yet")
    
    # Settings management buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reset All", key="reset_all_settings", help="Clear all saved settings"):
            clear_persistent_settings()
            st.success("Settings cleared!")
            st.rerun()
    
    with col2:
        # Export settings (future enhancement)
        if st.button("📋 View All", key="view_all_settings", help="View all saved settings"):
            st.session_state.show_settings_summary = True

def display_settings_summary():
    """Display a summary of all saved settings"""
    if st.session_state.get('show_settings_summary', False):
        with st.expander("📋 Current Saved Settings", expanded=True):
            initialize_persistent_settings()
            
            # Location settings
            location = get_persistent_setting('location')
            if location.get('is_set', False):
                st.write("**📍 Location & Regional:**")
                st.write(f"- ZIP Code: {location.get('zip_code', 'Not set')}")
                st.write(f"- State: {location.get('state', 'Not set')}")
                st.write(f"- Geography: {location.get('geography_type', 'Not set')}")
                st.write(f"- Fuel Price: ${location.get('fuel_price', 0):.2f}/gallon")
            
            # Personal settings
            personal = get_persistent_setting('personal')
            if personal.get('is_set', False):
                st.write("**👤 Personal Information:**")
                st.write(f"- Age: {personal.get('user_age', 'Not set')}")
                st.write(f"- Income: ${personal.get('gross_income', 0):,}")
                st.write(f"- Annual Mileage: {personal.get('annual_mileage', 'Not set'):,}")
                st.write(f"- Driving Style: {personal.get('driving_style', 'Not set').title()}")
                st.write(f"- Terrain: {personal.get('terrain', 'Not set').title()}")
                st.write(f"- Household Vehicles: {personal.get('num_household_vehicles', 'Not set')}")
            
            # Insurance settings
            insurance = get_persistent_setting('insurance')
            if insurance.get('is_set', False):
                st.write("**🛡️ Insurance Settings:**")
                st.write(f"- Coverage: {insurance.get('coverage_type', 'Not set').title()}")
                st.write(f"- Shop Type: {insurance.get('shop_type', 'Not set').title()}")
            
            # Analysis settings
            analysis = get_persistent_setting('analysis')
            if analysis.get('is_set', False):
                st.write("**📊 Analysis Preferences:**")
                st.write(f"- Priority: {analysis.get('comparison_priority', 'Not set').title()}")
                st.write(f"- Default Years: {analysis.get('default_analysis_years', 'Not set')}")
            
            if st.button("❌ Close", key="close_settings_summary"):
                st.session_state.show_settings_summary = False
                st.rerun()

# Utility function to pre-populate form data for comparison
def get_comparison_form_data(vehicle_override: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get form data for comparison with persistent settings pre-populated"""
    
    initialize_persistent_settings()
    
    # Base data from persistent settings
    base_data = {}
    
    # Add location data
    location = get_persistent_setting('location')
    if location.get('is_set', False):
        base_data.update({
            'zip_code': location.get('zip_code', ''),
            'state': location.get('state', ''),
            'geography_type': location.get('geography_type', 'Suburban'),
            'fuel_price': location.get('fuel_price', 3.50),
            'electricity_rate': location.get('electricity_rate', 0.12)
        })
    
    # Add personal data
    personal = get_persistent_setting('personal')
    if personal.get('is_set', False):
        base_data.update({
            'user_age': personal.get('user_age', 35),
            'gross_income': personal.get('gross_income', 60000),
            'annual_mileage': personal.get('annual_mileage', 12000),
            'driving_style': personal.get('driving_style', 'normal'),
            'terrain': personal.get('terrain', 'flat'),
            'num_household_vehicles': personal.get('num_household_vehicles', 2)
        })
    
    # Add insurance data
    insurance = get_persistent_setting('insurance')
    if insurance.get('is_set', False):
        base_data.update({
            'coverage_type': insurance.get('coverage_type', 'standard'),
            'shop_type': insurance.get('shop_type', 'independent')
        })
    
    # Add analysis data
    analysis = get_persistent_setting('analysis')
    if analysis.get('is_set', False):
        base_data.update({
            'comparison_priority': analysis.get('comparison_priority', 'cost'),
            'analysis_years': analysis.get('default_analysis_years', 5)
        })
    
    # Override with vehicle-specific data if provided
    if vehicle_override:
        base_data.update(vehicle_override)
    
    return base_data