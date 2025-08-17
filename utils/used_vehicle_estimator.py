# utils/used_vehicle_estimator.py

from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st
from models.depreciation.enhanced_depreciation import EnhancedDepreciationModel
from data.vehicle_database import VehicleDatabase

class UsedVehicleEstimator:
    """
    Estimates current market value for used vehicles based on depreciation calculations
    """
    
    def __init__(self):
        self.depreciation_model = EnhancedDepreciationModel()
        self.vehicle_db = VehicleDatabase()
        self.current_year = datetime.now().year
    
    def is_used_vehicle(self, year: int, current_mileage: int) -> bool:
        """
        Determine if a vehicle is considered used based on year and mileage
        
        Args:
            year: Model year of the vehicle
            current_mileage: Current odometer reading
            
        Returns:
            bool: True if vehicle is considered used
        """
        # Vehicle is used if:
        # 1. It's from a previous model year, OR
        # 2. It's current year but has significant mileage (>1000 miles for current year)
        
        if year < self.current_year:
            return True
        
        if year == self.current_year and current_mileage > 1000:
            return True
            
        return False
    
    def estimate_current_value(self, make: str, model: str, year: int, 
                             trim: str, current_mileage: int) -> Optional[float]:
        """
        Estimate current market value of a used vehicle
        
        Args:
            make: Vehicle manufacturer
            model: Vehicle model
            year: Model year
            trim: Trim level
            current_mileage: Current odometer reading
            
        Returns:
            float: Estimated current value, or None if cannot estimate
        """
        try:
            # Get original MSRP from vehicle database
            original_msrp = self._get_original_msrp(make, model, year, trim)
            if not original_msrp:
                return None
            
            # Calculate vehicle age
            vehicle_age = self.current_year - year
            if vehicle_age < 0:
                vehicle_age = 0
            
            # Estimate annual mileage based on current mileage and age
            if vehicle_age > 0:
                estimated_annual_mileage = current_mileage / vehicle_age
            else:
                # For current year vehicles, assume standard mileage rate
                estimated_annual_mileage = current_mileage * 4  # Quarterly estimation
            
            # Cap at reasonable maximum
            estimated_annual_mileage = min(estimated_annual_mileage, 30000)
            
            # Use depreciation model to calculate current value
            if vehicle_age == 0:
                # For current year vehicles, calculate depreciation based on mileage
                mileage_factor = self.depreciation_model._calculate_mileage_impact(
                    estimated_annual_mileage
                )
                # Apply simple mileage-based depreciation for new vehicles
                depreciation_rate = min(0.15, current_mileage / 100000 * 0.3)
                estimated_value = original_msrp * (1 - depreciation_rate) * mileage_factor
            else:
                # For older vehicles, use the full depreciation schedule
                depreciation_schedule = self.depreciation_model.calculate_depreciation_schedule(
                    initial_value=original_msrp,
                    vehicle_make=make,
                    vehicle_model=model,
                    model_year=year,
                    annual_mileage=estimated_annual_mileage,
                    years=vehicle_age
                )
                
                if depreciation_schedule:
                    estimated_value = depreciation_schedule[-1]['vehicle_value']
                else:
                    # Fallback calculation
                    estimated_value = original_msrp * (0.85 ** vehicle_age)
            
            # Apply additional mileage adjustment for high-mileage vehicles
            if current_mileage > estimated_annual_mileage * vehicle_age * 1.2:
                # High mileage penalty
                excess_mileage_factor = 0.95 - ((current_mileage - (12000 * max(vehicle_age, 1))) / 100000 * 0.1)
                estimated_value *= max(0.3, excess_mileage_factor)
            
            # Ensure minimum reasonable value (10% of original MSRP)
            estimated_value = max(estimated_value, original_msrp * 0.1)
            
            return round(estimated_value, 0)
            
        except Exception as e:
            st.error(f"Error estimating vehicle value: {str(e)}")
            return None
    
    def _get_original_msrp(self, make: str, model: str, year: int, trim: str) -> Optional[float]:
        """
        Get original MSRP for the vehicle from the database
        
        Args:
            make: Vehicle manufacturer
            model: Vehicle model  
            year: Model year
            trim: Trim level
            
        Returns:
            float: Original MSRP or None if not found
        """
        try:
            # Get vehicle data from database
            vehicle_data = self.vehicle_db.get_vehicle_data(make, model, year)
            
            if vehicle_data and 'trims' in vehicle_data:
                trim_data = vehicle_data['trims']
                
                # Try exact trim match first
                if trim in trim_data:
                    return trim_data[trim]
                
                # Try case-insensitive match
                for available_trim, price in trim_data.items():
                    if available_trim.lower() == trim.lower():
                        return price
                
                # If no exact match, return base trim price (typically the first/lowest)
                if trim_data:
                    return min(trim_data.values())
            
            return None
            
        except Exception as e:
            st.error(f"Error retrieving original MSRP: {str(e)}")
            return None
    
    def get_depreciation_insights(self, make: str, model: str, year: int, 
                                current_mileage: int, estimated_value: float) -> Dict[str, Any]:
        """
        Generate insights about the vehicle's depreciation and value
        
        Args:
            make: Vehicle manufacturer
            model: Vehicle model
            year: Model year  
            current_mileage: Current odometer reading
            estimated_value: Estimated current value
            
        Returns:
            dict: Depreciation insights and metrics
        """
        try:
            vehicle_age = self.current_year - year
            
            insights = {
                'vehicle_age': vehicle_age,
                'depreciation_assessment': self._assess_depreciation_rate(make, model, year, estimated_value),
                'mileage_assessment': self._assess_mileage_impact(current_mileage, vehicle_age),
                'value_retention_rating': self._get_value_retention_rating(make),
                'market_position': self._assess_market_position(estimated_value, make, model, year)
            }
            
            return insights
            
        except Exception as e:
            st.error(f"Error generating depreciation insights: {str(e)}")
            return {}
    
    def _assess_depreciation_rate(self, make: str, model: str, year: int, 
                                current_value: float) -> str:
        """Assess if depreciation rate is typical for the vehicle"""
        try:
            original_msrp = self._get_original_msrp(make, model, year, "Base")
            if not original_msrp:
                return "Cannot assess - original price unknown"
            
            depreciation_percentage = ((original_msrp - current_value) / original_msrp) * 100
            vehicle_age = self.current_year - year
            
            # Expected depreciation by age
            expected_depreciation = {
                1: 15, 2: 25, 3: 35, 4: 45, 5: 52, 
                6: 58, 7: 63, 8: 67, 9: 70, 10: 72
            }
            
            expected = expected_depreciation.get(vehicle_age, 75)
            
            if depreciation_percentage < expected - 5:
                return "Better than expected value retention"
            elif depreciation_percentage > expected + 10:
                return "Higher than typical depreciation"
            else:
                return "Normal depreciation rate for age"
                
        except:
            return "Cannot assess depreciation rate"
    
    def _assess_mileage_impact(self, current_mileage: int, vehicle_age: int) -> str:
        """Assess mileage impact on vehicle value"""
        if vehicle_age == 0:
            if current_mileage < 500:
                return "Very low mileage"
            elif current_mileage < 2000:
                return "Low mileage for current year"
            else:
                return "Higher mileage for current year"
        
        average_annual = current_mileage / vehicle_age if vehicle_age > 0 else 0
        
        if average_annual < 10000:
            return "Low mileage (below average)"
        elif average_annual < 15000:
            return "Average mileage"
        elif average_annual < 20000:
            return "Above average mileage"
        else:
            return "High mileage vehicle"
    
    def _get_value_retention_rating(self, make: str) -> str:
        """Get brand-based value retention rating"""
        # Based on brand multipliers from depreciation model
        brand_multipliers = {
            'Toyota': 'Excellent', 'Lexus': 'Excellent', 'Honda': 'Excellent',
            'Porsche': 'Excellent', 'Tesla': 'Good', 'Subaru': 'Good',
            'Mazda': 'Good', 'Hyundai': 'Average', 'Kia': 'Average',
            'Ford': 'Average', 'Chevrolet': 'Below Average', 'Chrysler': 'Poor'
        }
        
        return brand_multipliers.get(make, 'Average')
    
    def _assess_market_position(self, estimated_value: float, make: str, 
                              model: str, year: int) -> str:
        """Assess the vehicle's market position"""
        if estimated_value < 10000:
            return "Budget-friendly option"
        elif estimated_value < 25000:
            return "Mid-market value"
        elif estimated_value < 50000:
            return "Premium segment"
        else:
            return "Luxury/High-end market"


def integrate_used_vehicle_estimation():
    """
    Integration function to be called from the vehicle selection interface
    This should be added to the vehicle selection form where price input occurs
    """
    
    # Initialize the estimator
    estimator = UsedVehicleEstimator()
    
    # This would be integrated into the existing vehicle selection form
    # Example integration points:
    
    def on_vehicle_details_change(make, model, year, trim, current_mileage):
        """
        Callback function to execute when vehicle details change
        """
        if make and model and year and trim and current_mileage is not None:
            
            # Check if this is a used vehicle
            if estimator.is_used_vehicle(year, current_mileage):
                
                # Estimate current value
                estimated_value = estimator.estimate_current_value(
                    make, model, year, trim, current_mileage
                )
                
                if estimated_value:
                    # Auto-populate the purchase price field
                    st.session_state.estimated_price = estimated_value
                    
                    # Show estimation info to user
                    st.info(f"""
                    🔍 **Used Vehicle Detected**
                    
                    Estimated current market value: **${estimated_value:,.0f}**
                    
                    This estimate is based on:
                    - Vehicle age: {estimator.current_year - year} years
                    - Current mileage: {current_mileage:,} miles
                    - {make} {model} depreciation patterns
                    
                    💡 *This value has been automatically entered in the purchase price field*
                    """)
                    
                    # Get and display insights
                    insights = estimator.get_depreciation_insights(
                        make, model, year, current_mileage, estimated_value
                    )
                    
                    if insights:
                        with st.expander("📊 View Depreciation Analysis"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Vehicle Age", f"{insights['vehicle_age']} years")
                                st.write(f"**Mileage Assessment:** {insights['mileage_assessment']}")
                            
                            with col2:
                                st.write(f"**Value Retention:** {insights['value_retention_rating']}")
                                st.write(f"**Depreciation:** {insights['depreciation_assessment']}")
                            
                            st.write(f"**Market Position:** {insights['market_position']}")
                
                else:
                    st.warning("⚠️ Unable to estimate current value - vehicle data not found in database")
            
            else:
                # Clear any previous estimation
                if 'estimated_price' in st.session_state:
                    del st.session_state.estimated_price
    
    return on_vehicle_details_change


# Example of how to integrate this into the existing input form
def enhanced_vehicle_selection_with_price_estimation():
    """
    Enhanced vehicle selection form that includes automatic price estimation
    This would replace or enhance the existing vehicle selection interface
    """
    
    estimator = UsedVehicleEstimator()
    
    st.subheader("🚗 Vehicle Selection")
    
    # Vehicle selection inputs (simplified example)
    col1, col2 = st.columns(2)
    
    with col1:
        make = st.selectbox("Make", ["Tesla", "Toyota", "Honda", "Ford", "Chevrolet"])
        year = st.selectbox("Year", list(range(2024, 2015, -1)))
    
    with col2:
        model = st.selectbox("Model", ["Model 3", "Camry", "Civic", "F-150", "Silverado"])
        trim = st.selectbox("Trim", ["Base", "Performance", "LX", "EX"])
    
    # Mileage input
    current_mileage = st.number_input(
        "Current Mileage:",
        min_value=0,
        max_value=300000,
        value=0,
        step=1000,
        help="Current odometer reading"
    )
    
    # Purchase price with auto-estimation
    purchase_price = st.number_input(
        "Purchase Price ($):",
        min_value=1000,
        max_value=200000,
        value=st.session_state.get('estimated_price', 30000),
        step=500,
        help="Actual purchase price (auto-estimated for used vehicles)"
    )
    
    # Check for used vehicle and estimate price
    if make and model and year and trim and current_mileage is not None:
        
        if estimator.is_used_vehicle(year, current_mileage):
            
            estimated_value = estimator.estimate_current_value(
                make, model, year, trim, current_mileage
            )
            
            if estimated_value:
                # Update session state for price
                st.session_state.estimated_price = estimated_value
                
                # Rerun to update the input field
                if abs(purchase_price - estimated_value) > 1000:
                    st.rerun()
                
                # Show estimation details
                st.success(f"""
                ✅ **Used Vehicle Price Estimated**
                
                Current market value: **${estimated_value:,.0f}**
                
                You can adjust this price if you have a different offer or market data.
                """)
    
    return {
        'make': make,
        'model': model, 
        'year': year,
        'trim': trim,
        'current_mileage': current_mileage,
        'purchase_price': purchase_price
    }