"""
Enhanced Calculator Display with ALL Requested Features + Detailed Maintenance Breakdown + MPG Display
- ZIP code-based fuel/electricity pricing
- EV detection and charging style selection
- Maintenance duplicate removal and validation
- Specification-compliant variable names
- Comprehensive error handling and fallback modes
- Detailed maintenance schedule breakdown from calculator_display_10AUG.py
- Vehicle MPG database integration and UI display
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import pandas as pd

# Import with fallback handling
try:
    from ui.input_forms import collect_all_form_data
    from services.prediction_service import PredictionService
    from utils.session_manager import add_vehicle_to_comparison, save_calculation_results
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False

# Import MPG database functions
try:
    from data.vehicle_mpg_database import (
        get_vehicle_mpg, 
        get_mpg_display_text, 
        get_fuel_efficiency_rating,
        compare_mpg_to_class_average,
        estimate_annual_fuel_cost
    )
    MPG_DATABASE_AVAILABLE = True
except ImportError:
    MPG_DATABASE_AVAILABLE = False

def detect_electric_vehicle(make: str, model: str) -> bool:
    """Detect if make/model is an electric vehicle"""
    model_lower = model.lower()
    make_lower = make.lower()
    
    # Comprehensive EV model detection
    ev_models = [
        'leaf', 'model 3', 'model s', 'model x', 'model y', 'cybertruck',
        'bolt', 'volt', 'ioniq', 'kona electric', 'niro ev', 'soul ev',
        'i3', 'i4', 'ix', 'taycan', 'e-tron', 'id.4', 'mustang mach-e', 
        'lightning', 'polestar', 'ariya', 'ev6', 'lucid air'
    ]
    
    # Check for specific EV models
    for ev_model in ev_models:
        if ev_model in model_lower:
            return True
    
    # Check for EV keywords
    ev_keywords = ['electric', 'ev', 'plug-in', 'battery', 'bev']
    if any(keyword in model_lower for keyword in ev_keywords):
        return True
    
    # Tesla is all-electric
    if make_lower == 'tesla':
        return True
    
    return False

def get_vehicle_energy_type(make: str, model: str) -> str:
    """Determine vehicle energy type (gas, electric, hybrid)"""
    model_lower = model.lower()
    
    if detect_electric_vehicle(make, model):
        return 'electric'
    
    # Check for hybrid
    hybrid_keywords = ['hybrid', 'prius', 'insight', 'accord hybrid', 'camry hybrid']
    if any(keyword in model_lower for keyword in hybrid_keywords):
        return 'hybrid'
    
    return 'gasoline'

def display_vehicle_mpg_info(make: str, model: str, year: int, trim: str = None):
    """Display comprehensive MPG information for the selected vehicle"""
    
    if not MPG_DATABASE_AVAILABLE:
        st.info("💡 MPG database not available - using estimates")
        return
    
    # Get MPG data
    mpg_data = get_vehicle_mpg(make, model, year, trim)
    
    if mpg_data:
        # Create MPG display section
        st.markdown("---")
        st.subheader("⛽ Fuel Economy Information")
        
        # Main MPG display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            display_text = get_mpg_display_text(mpg_data)
            st.metric("Fuel Economy", display_text)
        
        with col2:
            efficiency_rating = get_fuel_efficiency_rating(mpg_data)
            rating_color = {
                "Excellent": "🟢",
                "Good": "🟡", 
                "Fair": "🟠",
                "Poor": "🔴"
            }
            st.metric("Efficiency Rating", f"{rating_color.get(efficiency_rating, '⚪')} {efficiency_rating}")
        
        with col3:
            data_source = mpg_data.get('source', 'unknown')
            source_labels = {
                'database': 'EPA Data',
                'database_trim_specific': 'EPA (Trim Specific)',
                'database_default_trim': 'EPA (Model Average)',
                'estimated': 'Estimated'
            }
            st.metric("Data Source", source_labels.get(data_source, 'Estimated'))
        
        # Detailed breakdown for non-electric vehicles
        if not mpg_data.get('is_electric', False):
            with st.expander("📊 Detailed MPG Breakdown"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("City MPG", f"{mpg_data.get('city', 0)}")
                with col2:
                    st.metric("Highway MPG", f"{mpg_data.get('highway', 0)}")
                with col3:
                    st.metric("Combined MPG", f"{mpg_data.get('combined', 0)}")
        
        # Class comparison
        comparison = compare_mpg_to_class_average(mpg_data, make, model)
        
        if comparison:
            with st.expander("🎯 Class Comparison"):
                st.write(f"**Vehicle Class:** {comparison['class_name']}")
                st.write(f"**Class Average:** {comparison['class_average']} {'MPGe' if mpg_data.get('is_electric') else 'MPG'}")
                
                if comparison['comparison'] == 'above':
                    st.success(f"✅ This vehicle is {comparison['difference']:.1f} {'MPGe' if mpg_data.get('is_electric') else 'MPG'} **above** the class average!")
                else:
                    st.warning(f"⚠️ This vehicle is {comparison['difference']:.1f} {'MPGe' if mpg_data.get('is_electric') else 'MPG'} **below** the class average.")
        
        return mpg_data
    
    return None

def display_fuel_cost_estimate(mpg_data: Dict[str, Any], annual_mileage: int, fuel_price: float, electricity_rate: float = 0.12):
    """Display estimated annual fuel costs based on MPG data"""
    
    if not mpg_data:
        return
    
    # Calculate annual cost
    annual_cost = estimate_annual_fuel_cost(mpg_data, annual_mileage, fuel_price, electricity_rate)
    monthly_cost = annual_cost / 12
    cost_per_mile = annual_cost / annual_mileage if annual_mileage > 0 else 0
    
    st.markdown("#### 💰 Estimated Fuel Costs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Annual Cost", f"${annual_cost:.0f}")
    
    with col2:
        st.metric("Monthly Cost", f"${monthly_cost:.0f}")
    
    with col3:
        if mpg_data.get('is_electric'):
            st.metric("Cost per Mile", f"${cost_per_mile:.3f}")
        else:
            st.metric("Cost per Mile", f"${cost_per_mile:.3f}")
    
    # Show calculation details
    if mpg_data.get('is_electric'):
        mpge = mpg_data.get('mpge_combined', 120)
        kwh_per_mile = 33.7 / mpge if mpge > 0 else 0.28
        st.info(f"⚡ **Electric Vehicle**: {mpge} MPGe efficiency • {kwh_per_mile:.3f} kWh per mile • ${electricity_rate:.3f}/kWh rate")
    else:
        combined_mpg = mpg_data.get('combined', 25)
        annual_gallons = annual_mileage / combined_mpg if combined_mpg > 0 else 0
        st.info(f"⛽ **Gasoline Vehicle**: {combined_mpg} MPG efficiency • {annual_gallons:.0f} gallons/year • ${fuel_price:.2f}/gallon")
    
    return {
        'annual_cost': annual_cost,
        'monthly_cost': monthly_cost,
        'cost_per_mile': cost_per_mile
    }
    """Detect if make/model is an electric vehicle"""
    model_lower = model.lower()
    make_lower = make.lower()
    
    # Comprehensive EV model detection
    ev_models = [
        'leaf', 'model 3', 'model s', 'model x', 'model y', 'cybertruck',
        'bolt', 'volt', 'ioniq', 'kona electric', 'niro ev', 'soul ev',
        'i3', 'i4', 'ix', 'taycan', 'e-tron', 'id.4', 'mustang mach-e', 
        'lightning', 'polestar', 'ariya', 'ev6', 'lucid air'
    ]
    
    # Check for specific EV models
    for ev_model in ev_models:
        if ev_model in model_lower:
            return True
    
    # Check for EV keywords
    ev_keywords = ['electric', 'ev', 'plug-in', 'battery', 'bev']
    if any(keyword in model_lower for keyword in ev_keywords):
        return True
    
    # Tesla is all-electric
    if make_lower == 'tesla':
        return True
    
    return False

def get_vehicle_energy_type(make: str, model: str) -> str:
    """Determine vehicle energy type (gas, electric, hybrid)"""
    model_lower = model.lower()
    
    if detect_electric_vehicle(make, model):
        return 'electric'
    
    # Check for hybrid
    hybrid_keywords = ['hybrid', 'prius', 'insight', 'accord hybrid', 'camry hybrid']
    if any(keyword in model_lower for keyword in hybrid_keywords):
        return 'hybrid'
    
    return 'gasoline'

def get_fuel_price_from_location(zip_code: str = None, state: str = None) -> float:
    """Get fuel price from ZIP code or state with regular/premium distinction"""
    # Base regular gas prices by state (current 2025 averages)
    state_regular_prices = {
        'CA': 4.65, 'TX': 3.25, 'FL': 3.40, 'NY': 3.85, 'IL': 3.60,
        'PA': 3.65, 'OH': 3.35, 'GA': 3.25, 'NC': 3.35, 'MI': 3.50,
        'WA': 4.20, 'OR': 4.10, 'NV': 4.05, 'AZ': 3.85, 'CO': 3.50,
        'MA': 3.75, 'TN': 3.30, 'IN': 3.45, 'MO': 3.35, 'WI': 3.55,
        'MN': 3.45, 'AL': 3.20, 'SC': 3.30, 'KY': 3.35, 'LA': 3.15
    }
    
    # ZIP code to state mapping for major metros (optional enhancement)
    zip_to_state = {
        '90210': 'CA', '10001': 'NY', '60601': 'IL', '77001': 'TX', '33101': 'FL',
        '98101': 'WA', '97201': 'OR', '80201': 'CO', '30301': 'GA', '48201': 'MI',
        '02101': 'MA', '37201': 'TN', '46201': 'IN', '63101': 'MO', '53201': 'WI',
        '55401': 'MN', '35201': 'AL', '29201': 'SC', '40201': 'KY', '70112': 'LA'
    }
    
    # Determine state from ZIP code if provided
    if zip_code and len(zip_code) == 5 and zip_code.isdigit():
        inferred_state = zip_to_state.get(zip_code, state)
        if inferred_state:
            state = inferred_state
    
    return state_regular_prices.get(state, 3.50)

def get_premium_fuel_price(regular_price: float) -> float:
    """Calculate premium fuel price (typically $0.30-$0.50 more than regular)"""
    return regular_price + 0.40

def determine_fuel_type_and_price(make: str, model: str, year: int, trim: str = "", 
                                 zip_code: str = None, state: str = None) -> Dict[str, Any]:
    """Determine if vehicle requires premium fuel and return appropriate pricing"""
    
    make_lower = make.lower()
    model_lower = model.lower()
    trim_lower = trim.lower()
    
    # Get base regular fuel price for location
    regular_price = get_fuel_price_from_location(zip_code, state)
    
    # Electric vehicles don't use fuel
    if detect_electric_vehicle(make, model):
        return {
            'fuel_type': 'electric',
            'fuel_price': 0.0,
            'requires_premium': False,
            'price_info': f"Electric vehicle - uses electricity instead of fuel"
        }
    
    # Determine if vehicle requires premium fuel
    requires_premium = False
    
    # 1. Luxury brands that typically require premium
    luxury_brands_premium = ['bmw', 'mercedes-benz', 'audi', 'lexus', 'infiniti', 'acura', 'porsche', 'maserati', 'alfa romeo']
    if make_lower in luxury_brands_premium:
        requires_premium = True
    
    # 2. Performance models that require premium
    performance_models = {
        'toyota': ['supra', 'prius prime'],
        'honda': ['type r', 'nsx', 'pilot elite'],
        'chevrolet': ['corvette', 'camaro ss', 'camaro zl1', 'tahoe rst'],
        'ford': ['mustang gt', 'mustang shelby', 'f-150 raptor', 'expedition platinum'],
        'hyundai': ['veloster n', 'genesis', 'santa fe calligraphy'],
        'nissan': ['gt-r', '370z', '400z', 'maxima platinum'],
        'subaru': ['wrx', 'sti', 'ascent touring'],
        'mazda': ['cx-90', 'cx-70'],
        'cadillac': ['cts-v', 'ats-v', 'escalade', 'ct4-v', 'ct5-v'],
        'dodge': ['hellcat', 'srt', 'viper', 'durango srt'],
        'jeep': ['srt', 'trackhawk', 'grand cherokee summit'],
        'buick': ['enclave avenir'],
        'gmc': ['yukon denali', 'sierra denali', 'acadia denali']
    }
    
    if make_lower in performance_models:
        for perf_model in performance_models[make_lower]:
            if perf_model in model_lower or perf_model in trim_lower:
                requires_premium = True
                break
    
    # 3. High-performance trims that require premium
    premium_trim_indicators = [
        'turbo', 'supercharged', 'v8', 'v10', 'v12', 'srt', 'ss', 'rs', 'sport',
        'performance', 'gt', 'gti', 'si', 'type r', 'nismo', 'sti', 'wrx',
        'amg', 'm sport', 'quattro', 's line', 'f sport', 'red sport', 'platinum',
        'denali', 'summit', 'calligraphy', 'avenir', 'touring', 'limited'
    ]
    
    for indicator in premium_trim_indicators:
        if indicator in trim_lower or indicator in model_lower:
            requires_premium = True
            break
    
    # 4. Specific high-end trims by make
    high_end_trims = {
        'toyota': ['limited', 'platinum', 'trd pro'],
        'honda': ['touring', 'elite'],
        'ford': ['platinum', 'king ranch', 'limited'],
        'chevrolet': ['high country', 'premier', 'ltz'],
        'gmc': ['denali', 'at4'],
        'ram': ['limited', 'laramie longhorn'],
        'jeep': ['summit', 'overland']
    }
    
    if make_lower in high_end_trims:
        for high_trim in high_end_trims[make_lower]:
            if high_trim in trim_lower:
                requires_premium = True
                break
    
    # Calculate final price
    if requires_premium:
        final_price = get_premium_fuel_price(regular_price)
        fuel_type = 'premium'
        price_info = f"Premium fuel required - ${final_price:.2f}/gal (${regular_price:.2f} regular + $0.40 premium)"
    else:
        final_price = regular_price
        fuel_type = 'regular'
        price_info = f"Regular fuel - ${final_price:.2f}/gal"
    
    return {
        'fuel_type': fuel_type,
        'fuel_price': final_price,
        'requires_premium': requires_premium,
        'regular_price': regular_price,
        'premium_price': get_premium_fuel_price(regular_price),
        'price_info': price_info
    }

def get_electricity_rate_from_location(zip_code: str = None, state: str = None) -> float:
    """Get electricity rate from ZIP code or state"""
    state_rates = {
        'CA': 0.17, 'TX': 0.10, 'FL': 0.11, 'NY': 0.15, 'IL': 0.12,
        'PA': 0.12, 'OH': 0.11, 'GA': 0.10, 'NC': 0.10, 'MI': 0.11,
        'WA': 0.08, 'OR': 0.09, 'HI': 0.28, 'AK': 0.22, 'CT': 0.18
    }
    return state_rates.get(state, 0.12) if state else 0.12

def clean_maintenance_services(services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicates and false items from maintenance services"""
    if not services:
        return []
    
    valid_services = []
    seen_services = set()
    
    for service in services:
        if not isinstance(service, dict):
            continue
            
        service_name = service.get('service', '').strip()
        total_cost = service.get('total_cost', service.get('cost', 0))
        
        # Skip invalid services (false items)
        if not service_name or total_cost <= 0:
            continue
            
        # Skip duplicates (normalized name)
        normalized_name = service_name.lower().replace('(', '').replace(')', '').strip()
        if normalized_name in seen_services:
            continue
            
        seen_services.add(normalized_name)
        valid_services.append({
            'service': service_name,
            'frequency': service.get('frequency', 1),
            'total_cost': total_cost,
            'cost_per_service': service.get('cost_per_service', total_cost),
            'type': service.get('type', 'routine')
        })
    
    return valid_services

def display_charging_preference_form() -> Dict[str, Any]:
    """Display charging preference form for electric vehicles"""
    
    st.subheader("🔌 EV Charging Preferences")
    
    charging_options = {
        'home_primary': '🏠 Home Primary (80% home, 15% workplace, 5% public)',
        'mixed': '⚡ Mixed Charging (60% home, 20% workplace, 20% public)', 
        'public_heavy': '🏢 Public Heavy (40% home, 10% workplace, 50% public)'
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        charging_preference = st.selectbox(
            "Primary Charging Style:",
            options=list(charging_options.keys()),
            format_func=lambda x: charging_options[x],
            index=1,
            help="How you plan to charge your EV affects electricity costs significantly"
        )
    
    with col2:
        st.info("**Cost Impact by Charging Style:**")
        st.write("🏠 Home Primary: ~$40-60/month")
        st.write("⚡ Mixed: ~$60-80/month") 
        st.write("🏢 Public Heavy: ~$100-130/month")
    
    return {'charging_preference': charging_preference}

def display_location_energy_info(zip_code: str = None, state: str = None, make: str = None, model: str = None, trim: str = None):
    """Display location and energy pricing info with EV detection"""
    
    is_electric = detect_electric_vehicle(make or '', model or '')
    energy_type = get_vehicle_energy_type(make or '', model or '')
    
    location_str = ""
    if zip_code and state:
        location_str = f"🗺️ Location: {zip_code}, {state}"
    elif state:
        location_str = f"🗺️ State: {state}"
    
    if is_electric:
        electricity_rate = get_electricity_rate_from_location(zip_code, state)
        st.info(f"{location_str} | 🔌 Electricity Rate: ${electricity_rate:.3f}/kWh | ⚡ Electric Vehicle")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Energy Type", "⚡ Electric")
        with col2:
            st.metric("Electricity Rate", f"${electricity_rate:.3f}/kWh")
        with col3:
            monthly_cost = electricity_rate * 300
            st.metric("Est. Monthly Energy", f"${monthly_cost:.0f}")
            
    elif energy_type == 'hybrid':
        fuel_price = get_fuel_price_from_location(zip_code, state)
        st.info(f"{location_str} | ⛽ Fuel Price: ${fuel_price:.2f}/gallon | 🔋 Hybrid Vehicle")
        
    else:
        fuel_price = get_fuel_price_from_location(zip_code, state)
        st.info(f"{location_str} | ⛽ Fuel Price: ${fuel_price:.2f}/gallon | 🚗 Gasoline Vehicle")

def display_maintenance_schedule_tab(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display detailed maintenance schedule and activities for each year (from calculator_display_10AUG.py)"""
    
    st.subheader("🔧 Detailed Maintenance Schedule")
    
    maintenance_schedule = results.get('maintenance_schedule', [])
    annual_breakdown = results.get('annual_breakdown', [])
    
    if not maintenance_schedule:
        st.warning("Maintenance schedule not available.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_maintenance_cost = sum(year['total_year_cost'] for year in maintenance_schedule)
    avg_annual_maintenance = total_maintenance_cost / len(maintenance_schedule) if maintenance_schedule else 0
    
    with col1:
        st.metric("Total Maintenance Cost", f"${total_maintenance_cost:,.0f}")
    
    with col2:
        st.metric("Average Annual", f"${avg_annual_maintenance:,.0f}")
    
    with col3:
        st.metric("Analysis Period", f"{len(maintenance_schedule)} years")
    
    with col4:
        shop_type = vehicle_data.get('shop_type', 'independent').title()
        st.metric("Service Type", shop_type)
    
    st.markdown("---")
    
    # Detailed year-by-year breakdown
    st.markdown("#### 📅 Year-by-Year Maintenance Activities")
    
    for year_data in maintenance_schedule:
        year_num = year_data['year']
        total_mileage = year_data['total_mileage']
        year_cost = year_data['total_year_cost']
        services = year_data.get('services', [])
        
        # Create expandable section for each year
        with st.expander(f"**Year {year_num}** ({total_mileage:,} miles) - ${year_cost:,.0f}", expanded=(year_num <= 2)):
            
            if not services:
                st.info("No maintenance activities scheduled for this year.")
                continue
            
            # Separate scheduled maintenance from wear/tear
            scheduled_services = [s for s in services if s.get('interval_based', True)]
            wear_services = [s for s in services if not s.get('interval_based', True)]
            
            # Display scheduled maintenance
            if scheduled_services:
                st.markdown("**🔧 Scheduled Maintenance:**")
                
                # Create a nice table for scheduled services
                service_data = []
                for service in scheduled_services:
                    service_data.append({
                        'Service': service['service'],
                        'Frequency': f"{service['frequency']}x",
                        'Cost Each': f"${service['cost_per_service']:,.0f}",
                        'Total Cost': f"${service['total_cost']:,.0f}",
                        'Type': service.get('shop_type', 'independent').title()
                    })
                
                if service_data:
                    df_services = pd.DataFrame(service_data)
                    st.dataframe(df_services, use_container_width=True, hide_index=True)
            
            # Display wear and tear items
            if wear_services:
                st.markdown("**⚙️ Wear & Tear / Repairs:**")
                
                for service in wear_services:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {service['service']}")
                    with col2:
                        st.write(f"${service['total_cost']:,.0f}")
            
            # Year summary
            scheduled_total = sum(s['total_cost'] for s in scheduled_services)
            wear_total = sum(s['total_cost'] for s in wear_services)
            
            if scheduled_total > 0 or wear_total > 0:
                st.markdown("**💰 Year Summary:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Scheduled Maintenance", f"${scheduled_total:,.0f}")
                with col2:
                    st.metric("Wear & Repairs", f"${wear_total:,.0f}")
                with col3:
                    st.metric("Year Total", f"${year_cost:,.0f}")
            
            # Show warranty coverage for leases
            if vehicle_data.get('transaction_type', '').lower() == 'lease':
                warranty_discount = year_data.get('warranty_discount', 0)
                if warranty_discount > 0:
                    warranty_savings = scheduled_total / (1 - warranty_discount) * warranty_discount
                    st.success(f"🛡️ Warranty Coverage: ${warranty_savings:,.0f} covered ({warranty_discount*100:.0f}%)")
    
    # Maintenance insights and recommendations
    st.markdown("---")
    st.markdown("#### 💡 Maintenance Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Cost Analysis:**")
        
        # Peak years analysis
        peak_year = max(maintenance_schedule, key=lambda x: x['total_year_cost'])
        low_year = min(maintenance_schedule, key=lambda x: x['total_year_cost'])
        
        st.write(f"• **Highest cost year:** Year {peak_year['year']} (${peak_year['total_year_cost']:,.0f})")
        st.write(f"• **Lowest cost year:** Year {low_year['year']} (${low_year['total_year_cost']:,.0f})")
        
        # Calculate cost trend
        first_half_avg = sum(y['total_year_cost'] for y in maintenance_schedule[:len(maintenance_schedule)//2]) / (len(maintenance_schedule)//2)
        second_half_avg = sum(y['total_year_cost'] for y in maintenance_schedule[len(maintenance_schedule)//2:]) / (len(maintenance_schedule) - len(maintenance_schedule)//2)
        
        if second_half_avg > first_half_avg * 1.2:
            st.write("• **Trend:** Costs increase significantly in later years")
        elif second_half_avg < first_half_avg * 0.8:
            st.write("• **Trend:** Costs decrease in later years (unusual)")
        else:
            st.write("• **Trend:** Costs remain relatively stable over time")
    
    with col2:
        st.markdown("**💰 Cost Optimization Tips:**")
        
        shop_type = vehicle_data.get('shop_type', 'independent')
        if shop_type == 'dealership':
            st.write("• Consider independent shops for routine maintenance to save 15-20%")
        elif shop_type == 'independent':
            st.write("• You're already optimizing costs with independent shops")
        
        st.write("• Follow manufacturer's maintenance schedule to prevent major repairs")
        st.write("• Keep detailed maintenance records for warranty and resale value")
        
        if vehicle_data.get('transaction_type', '').lower() == 'lease':
            st.write("• For leases, use dealership service to maintain warranty coverage")
        else:
            st.write("• Regular maintenance can extend vehicle life beyond analysis period")

def display_calculator():
    """Enhanced calculator with ALL requested features"""
    
    st.header("🔧 Single Vehicle Analysis")
    st.markdown("Calculate total cost of ownership with advanced features:")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🗺️ **ZIP Code Pricing**\nAuto-detects fuel/electricity rates")
    with col2:
        st.info("⚡ **EV Support**\nCharging style selection")
    with col3:
        st.info("🔧 **Clean Maintenance**\nDuplicate removal & validation")
    
    if not SERVICES_AVAILABLE:
        st.warning("⚠️ Some services not available - using enhanced basic calculator")
        display_enhanced_basic_calculator()
        return
    
    # Full calculator with all features
    display_full_featured_calculator()

def display_enhanced_basic_calculator():
    """Enhanced basic calculator with all requested features"""
    
    st.subheader("🚗 Enhanced Basic Vehicle Calculator")
    st.info("💡 All key features available! Install dependencies for advanced analysis.")
    
    # Enhanced form with all features
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚗 Vehicle Information**")
        make = st.selectbox("Make:", ["Tesla", "Toyota", "Honda", "Chevrolet", "Ford", "Hyundai", "BMW", "Nissan"])
        model = st.text_input("Model:", value="Model 3" if make == "Tesla" else "Camry")
        year = st.number_input("Year:", min_value=2015, max_value=2025, value=2024)
        
        is_electric = detect_electric_vehicle(make, model)
        
        if is_electric:
            st.success(f"⚡ Electric Vehicle Detected: {make} {model}")
            price = st.number_input("Purchase Price ($):", min_value=20000, max_value=200000, value=45000, step=1000)
        else:
            price = st.number_input("Purchase Price ($):", min_value=10000, max_value=200000, value=30000, step=1000)
        
        # Display MPG information if vehicle is selected
        if make and model and year:
            mpg_data = display_vehicle_mpg_info(make, model, year, trim)
    
    with col2:
        st.markdown("**📍 Location & Usage**")
        zip_code = st.text_input("ZIP Code (5 digits):", value="90210", help="Auto-populates fuel/electricity pricing")
        
        if zip_code and len(zip_code) == 5 and zip_code.isdigit():
            zip_to_state = {
                '90210': 'CA', '10001': 'NY', '60601': 'IL', '77001': 'TX', '33101': 'FL',
                '98101': 'WA', '97201': 'OR', '80201': 'CO', '30301': 'GA', '48201': 'MI'
            }
            state = zip_to_state.get(zip_code, 'CA')
        else:
            state = st.selectbox("State:", ['CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'], index=0)
        
        annual_mileage = st.number_input("Annual Mileage:", min_value=5000, max_value=50000, value=12000, step=1000)
        analysis_years = st.number_input("Analysis Years:", min_value=1, max_value=15, value=5)
    
    # Display location and energy info
    display_location_energy_info(zip_code, state, make, model, trim)
    
    # EV-specific charging preferences
    charging_data = {}
    if is_electric:
        st.markdown("---")
        charging_data = display_charging_preference_form()
    
    # Calculate button
    if st.button("🚀 Calculate Enhanced TCO", type="primary", use_container_width=True):
        
        if is_electric:
            electricity_rate = get_electricity_rate_from_location(zip_code, state)
            fuel_price = 0
        else:
            fuel_price = get_fuel_price_from_location(zip_code, state)
            electricity_rate = 0
        
        results = calculate_enhanced_tco(
            make=make,
            model=model,
            year=year,
            price=price,
            annual_mileage=annual_mileage,
            years=analysis_years,
            fuel_price=fuel_price,
            electricity_rate=electricity_rate,
            is_electric=is_electric,
            charging_preference=charging_data.get('charging_preference', 'mixed'),
            zip_code=zip_code,
            state=state
        )
        
        display_enhanced_results(results, make, model, year, is_electric)

def calculate_enhanced_tco(make: str, model: str, year: int, price: float, annual_mileage: int, 
                          years: int, fuel_price: float, electricity_rate: float, is_electric: bool,
                          charging_preference: str, zip_code: str, state: str, 
                          current_mileage: int = 0) -> Dict[str, Any]:
    """
    Enhanced TCO calculation with all features.
    FIXED: Added the missing calculation logic before displaying results.
    """
    
    try:
        # FIXED: ADD THE MISSING CALCULATION LOGIC FIRST
        from datetime import datetime
        current_year = datetime.now().year
        purchase_year = current_year
        
        # Create input data for PredictionService (same pattern as your working code)
        enhanced_form_data = {
            'make': make,
            'model': model,
            'year': year,
            'price': price,
            'trim_msrp': price,  # Use actual price as MSRP for calculations
            'current_mileage': current_mileage,  # Support starting mileage
            'annual_mileage': annual_mileage,
            'analysis_years': years,
            'zip_code': zip_code,
            'state': state,
            'transaction_type': 'purchase',
            'fuel_price': fuel_price,
            'electricity_rate': electricity_rate,
            'is_electric': is_electric,
            'charging_preference': charging_preference
        }
        
        # FIXED: USE PredictionService TO ACTUALLY CALCULATE THE RESULTS
        from services.prediction_service import PredictionService
        prediction_service = PredictionService()
        
        # Calculate full TCO with enhanced features
        raw_results = prediction_service.calculate_total_cost_of_ownership(enhanced_form_data)
        
        # Clean maintenance data to remove duplicates
        if 'maintenance_schedule' in raw_results:
            for year_data in raw_results['maintenance_schedule']:
                if 'services' in year_data:
                    year_data['services'] = clean_maintenance_services(year_data['services'])
        
        # FIXED: CREATE THE RESULTS STRUCTURE THAT THE DISPLAY CODE EXPECTS
        summary = raw_results.get('summary', {})
        category_totals = raw_results.get('category_totals', {})
        
        results = {
            'total_cost': summary.get('total_ownership_cost', 0),
            'annual_cost': summary.get('average_annual_cost', 0),
            'cost_per_mile': summary.get('cost_per_mile', 0),
            'final_value': summary.get('final_vehicle_value', 0),
            'depreciation': category_totals.get('depreciation', 0),
            'maintenance': category_totals.get('maintenance', 0),
            'insurance': category_totals.get('insurance', 0),
            'energy': category_totals.get('fuel_energy', 0),
            'annual_operating_cost': category_totals.get('maintenance', 0) + category_totals.get('insurance', 0) + category_totals.get('fuel_energy', 0),
            'annual_energy_cost': category_totals.get('fuel_energy', 0) / years if years > 0 else 0,
            'is_electric': is_electric,
            'charging_preference': charging_preference,
            'location': {'zip_code': zip_code, 'state': state},
            'maintenance_schedule': raw_results.get('maintenance_schedule', []),
            'annual_breakdown': raw_results.get('annual_breakdown', []),
            'vehicle_info': raw_results.get('vehicle_info', {})
        }
        
        # NOW DISPLAY THE RESULTS (your existing display code)
        st.success("✅ Enhanced TCO calculation completed with all features!")
        
        # Vehicle header with energy type
        energy_icon = "⚡" if is_electric else "⛽"
        st.subheader(f"📊 {year} {make} {model} {energy_icon}")
        
        # Enhanced summary metrics - SEPARATED operating costs from total TCO
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total TCO", f"${results['total_cost']:,.0f}", help="Total Cost of Ownership including depreciation")
        with col2:
            st.metric("Annual Operating Cost", f"${results['annual_cost']:,.0f}", help="Direct annual expenses (no depreciation)")
        with col3:
            st.metric("Operating Cost/Mile", f"${results['cost_per_mile']:.3f}", help="Direct costs per mile driven")
        with col4:
            st.metric("Final Value", f"${results['final_value']:,.0f}", help="Estimated vehicle value at end of period")
        
        # Enhanced cost breakdown - CLEARLY SEPARATE operating vs total costs
        st.subheader("💰 Cost Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📅 Annual Operating Costs** *(Direct expenses)*")
            st.metric("Maintenance", f"${results['maintenance'] / years:,.0f}/year")
            st.metric("Insurance", f"${results['insurance'] / years:,.0f}/year")
            energy_label = "Electricity" if results['is_electric'] else "Fuel"
            st.metric(energy_label, f"${results['energy'] / years:,.0f}/year")
            
            annual_operating = results['annual_operating_cost'] / years
            st.metric("**Total Operating**", f"${annual_operating:,.0f}/year", help="Annual out-of-pocket expenses")
        
        with col2:
            st.markdown("**📈 Total Cost of Ownership** *(Includes opportunity cost)*")
            st.metric("Depreciation", f"${results['depreciation']:,.0f} total", help="Opportunity cost - not a direct expense")
            st.metric("Operating Costs", f"${results['annual_operating_cost']:,.0f} total")
            st.metric("**Total TCO**", f"${results['total_cost']:,.0f}", help="Complete ownership cost including depreciation")
            
            # Show what matters for budgeting
            st.info("💡 **For budgeting**: Focus on Annual Operating Cost (${:,.0f}/year)".format(results['annual_cost']))
        
        # Location and energy info
        location = results['location']
        st.info(f"📍 Pricing based on ZIP: {location['zip_code']}, {location['state']} | "
                f"Annual Energy Cost: ${results['annual_energy_cost']:,.0f}")
        
        if is_electric and results['charging_preference']:
            st.info(f"🔌 Charging Style: {results['charging_preference'].replace('_', ' ').title()}")
        
        # Tabs for detailed results including maintenance
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Cost Summary", 
            "🔧 Detailed Maintenance",  # NEW TAB
            "📈 Visualizations", 
            "💡 Insights"
        ])
        
        with tab1:
            # Enhanced visualization - FOCUS ON OPERATING COSTS
            operating_categories = ['Maintenance', 'Insurance', energy_label]
            operating_values = [
                results['maintenance'],
                results['insurance'], 
                results['energy']
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Annual Operating Costs Breakdown**")
                fig_operating = go.Figure(data=[go.Pie(labels=operating_categories, values=operating_values, hole=0.3)])
                fig_operating.update_layout(title="Direct Annual Expenses", height=300)
                st.plotly_chart(fig_operating, use_container_width=True)
            
            with col2:
                st.markdown("**Total Cost of Ownership**")
                total_categories = ['Depreciation'] + operating_categories
                total_values = [results['depreciation']] + operating_values
                
                fig_total = go.Figure(data=[go.Pie(labels=total_categories, values=total_values, hole=0.3)])
                fig_total.update_layout(title="Complete TCO Analysis", height=300)
                st.plotly_chart(fig_total, use_container_width=True)
        
        with tab2:
            # Display detailed maintenance schedule using the new function
            # Create a mock vehicle_data dict for the maintenance tab
            vehicle_data = {
                'make': make,
                'model': model,
                'year': year,
                'shop_type': 'independent',
                'transaction_type': 'purchase'
            }
            display_maintenance_schedule_tab(results, vehicle_data)
        
        with tab3:
            # Enhanced visualizations
            st.subheader("📈 Cost Analysis Charts")
            
            # Annual cost breakdown chart with CORRECT years
            if 'maintenance_schedule' in results and 'annual_breakdown' in results:
                annual_data = results['annual_breakdown']
                
                if annual_data:
                    # Extract data for visualization
                    ownership_years = [year_data['ownership_year'] for year_data in annual_data]
                    maintenance_costs = [year_data['annual_maintenance'] for year_data in annual_data]
                    depreciation_costs = [year_data['annual_depreciation'] for year_data in annual_data]
                    insurance_costs = [year_data['annual_insurance'] for year_data in annual_data]
                    energy_costs = [year_data['annual_energy'] for year_data in annual_data]
                    
                    fig_annual = go.Figure()
                    
                    fig_annual.add_trace(go.Bar(
                        x=ownership_years,
                        y=maintenance_costs,
                        name='Maintenance',
                        marker_color='lightblue'
                    ))
                    
                    fig_annual.add_trace(go.Bar(
                        x=ownership_years,
                        y=depreciation_costs,
                        name='Depreciation',
                        marker_color='lightcoral'
                    ))
                    
                    fig_annual.add_trace(go.Bar(
                        x=ownership_years,
                        y=insurance_costs,
                        name='Insurance',
                        marker_color='lightgreen'
                    ))
                    
                    fig_annual.add_trace(go.Bar(
                        x=ownership_years,
                        y=energy_costs,
                        name=energy_label,
                        marker_color='gold'
                    ))
                    
                    fig_annual.update_layout(
                        title="Annual Cost Breakdown by Ownership Year",
                        xaxis_title="Calendar Year",
                        yaxis_title="Annual Cost ($)",
                        barmode='stack',
                        height=400
                    )
                    
                    st.plotly_chart(fig_annual, use_container_width=True)
                    
                    # Add vehicle age context
                    vehicle_info = results.get('vehicle_info', {})
                    model_year = vehicle_info.get('model_year', year)
                    current_year = vehicle_info.get('current_year', 2025)
                    
                    st.info(f"📅 **Vehicle Timeline**: {model_year} {make} {model} purchased in {current_year}")
                    st.write(f"• **Vehicle Age at Purchase**: {current_year - model_year} years old")
                    if annual_data:
                        final_year = annual_data[-1]['ownership_year']
                        final_age = final_year - model_year
                        st.write(f"• **Vehicle Age at End of Analysis**: {final_age} years old ({final_year})")
            
            else:
                # Fallback visualization using maintenance_schedule
                years_list = [year_data['year'] for year_data in results['maintenance_schedule']]
                maintenance_costs = [year_data['total_year_cost'] for year_data in results['maintenance_schedule']]
                
                # Calculate other annual costs (simplified)
                annual_depreciation = results['depreciation'] / len(years_list)
                annual_insurance = results['insurance'] / len(years_list)
                annual_energy = results['energy'] / len(years_list)
                
                fig_annual = go.Figure()
                
                fig_annual.add_trace(go.Bar(
                    x=years_list,
                    y=maintenance_costs,
                    name='Maintenance',
                    marker_color='lightblue'
                ))
                
                fig_annual.add_trace(go.Bar(
                    x=years_list,
                    y=[annual_depreciation] * len(years_list),
                    name='Depreciation',
                    marker_color='lightcoral'
                ))
                
                fig_annual.add_trace(go.Bar(
                    x=years_list,
                    y=[annual_insurance] * len(years_list),
                    name='Insurance',
                    marker_color='lightgreen'
                ))
                
                fig_annual.add_trace(go.Bar(
                    x=years_list,
                    y=[annual_energy] * len(years_list),
                    name=energy_label,
                    marker_color='gold'
                ))
                
                fig_annual.update_layout(
                    title="Annual Cost Breakdown by Year of Ownership",
                    xaxis_title="Year of Ownership",
                    yaxis_title="Annual Cost ($)",
                    barmode='stack',
                    height=400
                )
                
                st.plotly_chart(fig_annual, use_container_width=True)
        
        with tab4:
            # Enhanced insights
            st.subheader("💡 Enhanced Insights")
            
            insights = []
            
            if is_electric:
                if results['charging_preference'] == 'home_primary':
                    insights.append("🏠 Excellent choice! Home charging provides lowest energy costs")
                elif results['charging_preference'] == 'public_heavy':
                    insights.append("🏢 Consider home charging installation to reduce costs by 40-60%")
                
                insights.append("⚡ Electric vehicles have lower maintenance costs (no oil changes)")
                insights.append("🔋 Battery replacement may be needed after 8-10 years")
            else:
                insights.append("⛽ Consider fuel-efficient driving to improve MPG by 10-15%")
                insights.append("🔧 Regular maintenance prevents costly repairs")
            
            insights.append(f"📍 Location-based pricing: {location['state']} rates applied")
            insights.append("🔍 Maintenance schedule cleaned of duplicates and validated")
            
            for insight in insights:
                st.info(insight)
            
            # Feature showcase
            st.markdown("---")
            st.success("🚀 **All Features Active!** ZIP code pricing, EV detection, charging styles, detailed maintenance breakdown, and clean maintenance data")
        
        # FIXED: RETURN THE RESULTS (this was missing!)
        return raw_results
        
    except Exception as e:
        # Enhanced error handling 
        st.error(f"❌ Calculation failed: {str(e)}")
        st.error("Please check your inputs and try again.")
        
        # Return basic fallback result
        return {
            'summary': {'total_ownership_cost': 0, 'average_annual_cost': 0},
            'category_totals': {},
            'annual_breakdown': [],
            'maintenance_schedule': []
        }


def display_full_featured_calculator():
    """Full calculator with all services available"""
    
    st.subheader("🚗 Advanced Vehicle Calculator")
    st.success("✅ All services available - full functionality enabled")
    
    # Create two columns: form and results
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        form_data, is_valid, message = collect_all_form_data()
        
        # Add EV charging preference if electric vehicle detected
        if is_valid and detect_electric_vehicle(form_data.get('make', ''), form_data.get('model', '')):
            st.markdown("---")
            charging_data = display_charging_preference_form()
            form_data.update(charging_data)
        
        if not is_valid:
            st.warning(f"⚠️ {message}")
            return
        
        # Enhanced location display with reactive fuel pricing
        zip_code = form_data.get('zip_code', '')
        state = form_data.get('state', '')
        make = form_data.get('make', '')
        model = form_data.get('model', '')
        trim = form_data.get('trim', '')
        
        # Show current fuel pricing based on selections
        if make and model and state:
            st.markdown("---")
            st.subheader("📍 Current Pricing Information")
            
            vehicle_is_electric = detect_electric_vehicle(make, model)
            
            if vehicle_is_electric:
                electricity_rate = get_electricity_rate_from_location(zip_code, state)
                st.info(f"⚡ **Electric Vehicle**: {make} {model} - Electricity rate in {state}: ${electricity_rate:.3f}/kWh")
            else:
                fuel_info = determine_fuel_type_and_price(make, model, form_data.get('year', 2024), trim, zip_code, state)
                if fuel_info['requires_premium']:
                    st.warning(f"🔥 **Premium Fuel Required**: {make} {model} {trim} - {fuel_info['price_info']} in {state}")
                else:
                    st.success(f"⛽ **Regular Fuel**: {make} {model} {trim} - {fuel_info['price_info']} in {state}")
                
                # Show comparison if premium required
                if fuel_info['requires_premium']:
                    with st.expander("💰 Regular vs Premium Fuel Cost Comparison"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Regular Price", f"${fuel_info['regular_price']:.2f}/gal")
                        with col2:
                            st.metric("Premium Price", f"${fuel_info['premium_price']:.2f}/gal")
                        with col3:
                            extra_cost = fuel_info['premium_price'] - fuel_info['regular_price']
                            st.metric("Extra Cost", f"${extra_cost:.2f}/gal")
                        
                        # Calculate annual impact
                        annual_mileage = form_data.get('annual_mileage', 12000)
                        estimated_mpg = 25  # Conservative estimate
                        annual_gallons = annual_mileage / estimated_mpg
                        annual_extra_cost = annual_gallons * extra_cost
                        st.info(f"📊 **Estimated Annual Premium Fuel Cost**: ${annual_extra_cost:.0f} more than regular fuel")
            
            display_location_energy_info(zip_code, state, make, model, trim)
        elif state:
            # Show state-level pricing when vehicle not fully selected
            st.markdown("---")
            regular_price = get_fuel_price_from_location(None, state)
            premium_price = get_premium_fuel_price(regular_price)
            electricity_rate = get_electricity_rate_from_location(None, state)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"Regular Fuel ({state})", f"${regular_price:.2f}/gal")
            with col2:
                st.metric(f"Premium Fuel ({state})", f"${premium_price:.2f}/gal")
            with col3:
                st.metric(f"Electricity ({state})", f"${electricity_rate:.3f}/kWh")
            
            st.info("💡 Complete vehicle selection to see specific fuel requirements")
        
        # Calculate button
        if st.button("🚀 Calculate Enhanced TCO", type="primary", use_container_width=True):
            with st.spinner("Calculating with all enhanced features..."):
                try:
                    # Get vehicle information for fuel pricing
                    make = form_data.get('make', '')
                    model = form_data.get('model', '')
                    year = form_data.get('year', 2024)
                    trim = form_data.get('trim', '')
                    zip_code = form_data.get('zip_code', '')
                    state = form_data.get('state', '')
                    
                    # Detect if vehicle is electric
                    vehicle_is_electric = detect_electric_vehicle(make, model)
                    
                    # Enhance form data with location-based pricing and smart fuel detection
                    enhanced_form_data = form_data.copy()
                    
                    if vehicle_is_electric:
                        enhanced_form_data['electricity_rate'] = get_electricity_rate_from_location(zip_code, state)
                        enhanced_form_data['fuel_price'] = 0.0
                        enhanced_form_data['is_electric'] = True
                        st.success(f"⚡ Electric vehicle detected - using electricity rate: ${enhanced_form_data['electricity_rate']:.3f}/kWh")
                    else:
                        # Get smart fuel pricing based on vehicle specs
                        fuel_info = determine_fuel_type_and_price(make, model, year, trim, zip_code, state)
                        enhanced_form_data['fuel_price'] = fuel_info['fuel_price']
                        enhanced_form_data['fuel_type'] = fuel_info['fuel_type']
                        enhanced_form_data['requires_premium'] = fuel_info['requires_premium']
                        enhanced_form_data['electricity_rate'] = get_electricity_rate_from_location(zip_code, state)
                        enhanced_form_data['is_electric'] = False
                        
                        # Show pricing information
                        if enhanced_form_data['requires_premium']:
                            st.warning(f"🔥 Premium fuel required - using premium pricing: ${enhanced_form_data['fuel_price']:.2f}/gal")
                        else:
                            st.success(f"⛽ Regular fuel detected - using regular pricing: ${enhanced_form_data['fuel_price']:.2f}/gal")
                    
                    # Perform calculation
                    prediction_service = PredictionService()
                    results = prediction_service.calculate_total_cost_of_ownership(enhanced_form_data)
                    
                    # Clean maintenance data
                    if 'maintenance_schedule' in results:
                        for year_data in results['maintenance_schedule']:
                            if 'services' in year_data:
                                year_data['services'] = clean_maintenance_services(year_data['services'])
                    
                    # Save results to session state
                    st.session_state.current_vehicle = enhanced_form_data
                    st.session_state.current_results = results
                    st.session_state.calculation_complete = True
                    
                    save_calculation_results(enhanced_form_data, results)
                    
                    st.success("✅ Enhanced calculation completed with all features!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Calculation failed: {str(e)}")
                    st.error("Please check your inputs and try again.")
        
        # Add to comparison button - RIGHT NEXT TO CALCULATE BUTTON
        st.markdown("#### 🔄 Vehicle Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Add to Comparison List** to evaluate multiple vehicles side-by-side")
        
        with col2:
            if st.button("➕ Add to Comparison", type="secondary", use_container_width=True, key="add_comparison_full"):
                # Create vehicle data for comparison
                vehicle_data = form_data.copy()
                
                try:
                    if 'comparison_vehicles' not in st.session_state:
                        st.session_state.comparison_vehicles = []
                    
                    # Check for duplicates
                    make = vehicle_data.get('make', '')
                    model = vehicle_data.get('model', '')
                    year = vehicle_data.get('year', '')
                    trim = vehicle_data.get('trim', '')
                    
                    vehicle_exists = any(
                        existing.get('make') == make and 
                        existing.get('model') == model and 
                        existing.get('year') == year and 
                        existing.get('trim') == trim
                        for existing in st.session_state.comparison_vehicles
                    )
                    
                    if not vehicle_exists:
                        st.session_state.comparison_vehicles.append(vehicle_data)
                        st.success(f"✅ Added {year} {make} {model} {trim} to comparison list!")
                        st.balloons()
                        st.info(f"🔍 Comparison list now has {len(st.session_state.comparison_vehicles)} vehicles")
                    else:
                        st.warning("⚠️ This vehicle is already in your comparison list!")
                        
                except Exception as e:
                    st.error(f"Error adding to comparison: {str(e)}")
    
    with col2:
        # Display enhanced quick summary if available
        if st.session_state.get('calculation_complete', False):
            st.subheader("📊 Quick Summary")
            
            results = st.session_state.current_results
            vehicle_data = st.session_state.current_vehicle
            
            # Vehicle info
            make = vehicle_data.get('make', '')
            model = vehicle_data.get('model', '')
            year = vehicle_data.get('year', '')
            
            is_electric = detect_electric_vehicle(make, model)
            energy_icon = "⚡" if is_electric else "⛽"
            
            st.markdown(f"**{year} {make} {model} {energy_icon}**")
            
            # Key metrics
            if vehicle_data.get('transaction_type') == 'Purchase':
                total_cost = results['summary']['total_ownership_cost']
                annual_cost = results['summary']['average_annual_cost']
                
                st.metric("Total Cost", f"${total_cost:,.0f}")
                st.metric("Annual Cost", f"${annual_cost:,.0f}")
            
            # REMOVED: The red "Add to Comparison" button that was here
        else:
            st.info("👈 Complete the form and click 'Calculate Enhanced TCO' to see results")
    
    # Display detailed results if calculation is complete
    if st.session_state.get('calculation_complete', False):
        st.markdown("---")
        display_detailed_results_with_maintenance()

def display_quick_summary():
    """Display a quick summary card of the calculation"""
    
    if not st.session_state.get('current_results'):
        return
    
    results = st.session_state.current_results
    vehicle_data = st.session_state.current_vehicle
    
    st.subheader("📊 Quick Summary")
    
    # Vehicle info
    make = vehicle_data.get('make', '')
    model = vehicle_data.get('model', '')
    year = vehicle_data.get('year', '')
    
    is_electric = detect_electric_vehicle(make, model)
    energy_icon = "⚡" if is_electric else "⛽"
    
    st.markdown(f"**{year} {make} {model} {energy_icon}**")
    
    # Key metrics
    if vehicle_data.get('transaction_type') == 'Purchase':
        total_cost = results['summary']['total_ownership_cost']
        annual_cost = results['summary']['average_annual_cost']
        
        st.metric("Total Cost", f"${total_cost:,.0f}")
        st.metric("Annual Cost", f"${annual_cost:,.0f}")

def display_detailed_results_with_maintenance():
    """Display comprehensive analysis results with enhanced maintenance tab"""
    
    results = st.session_state.current_results
    vehicle_data = st.session_state.current_vehicle
    
    # Tabs for organized display - NOW INCLUDING DETAILED MAINTENANCE
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Summary", 
        "🔧 Detailed Maintenance",  # Enhanced maintenance tab
        "📈 Visualizations", 
        "💰 Cost Breakdown",
        "🎯 Recommendations"
    ])
    
    with tab1:
        display_summary_tab(results, vehicle_data)
    
    with tab2:
        # NEW: Use the detailed maintenance schedule function
        display_maintenance_schedule_tab(results, vehicle_data)
    
    with tab3:
        display_visualizations(results, vehicle_data)
    
    with tab4:
        display_cost_breakdown(results, vehicle_data)
    
    with tab5:
        display_recommendations_tab(results, vehicle_data)

def display_summary_tab(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display summary information"""
    
    st.subheader("📊 Cost Summary")
    
    # Summary metrics based on transaction type
    if vehicle_data.get('transaction_type') == 'Purchase':
        summary = results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cost", f"${summary['total_ownership_cost']:,.0f}")
        with col2:
            st.metric("Annual Average", f"${summary['average_annual_cost']:,.0f}")
        with col3:
            st.metric("Cost per Mile", f"${summary['cost_per_mile']:.3f}")
        with col4:
            st.metric("Final Value", f"${summary.get('final_vehicle_value', 0):,.0f}")
    
    else:  # Lease
        summary = results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Lease Cost", f"${summary['total_lease_cost']:,.0f}")
        with col2:
            st.metric("Monthly Average", f"${summary['average_monthly_cost']:,.0f}")
        with col3:
            st.metric("Cost per Mile", f"${summary['cost_per_mile']:.3f}")
        with col4:
            down_payment = summary.get('down_payment', 0)
            st.metric("Down Payment", f"${down_payment:,.0f}")
    
    # Category breakdown
    st.markdown("#### Cost Categories")
    category_totals = results.get('category_totals', {})
    
    if category_totals:
        categories = list(category_totals.keys())
        mid_point = len(categories) // 2
        
        col1, col2 = st.columns(2)
        
        with col1:
            for category in categories[:mid_point]:
                st.metric(
                    category.replace('_', ' ').title(),
                    f"${category_totals[category]:,.0f}"
                )
        
        with col2:
            for category in categories[mid_point:]:
                st.metric(
                    category.replace('_', ' ').title(),
                    f"${category_totals[category]:,.0f}"
                )

def display_visualizations(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display charts and visualizations"""
    
    st.subheader("📊 Cost Visualizations")
    
    # Annual costs over time
    breakdown_data = results.get('annual_breakdown', [])
    if breakdown_data:
        df = pd.DataFrame(breakdown_data)
        
        # Line chart of annual costs
        fig_line = go.Figure()
        
        cost_categories = [col for col in df.columns if col not in ['ownership_year', 'year_of_ownership', 'vehicle_age', 'vehicle_model_year', 'total_mileage', 'total_annual_operating_cost', 'total_annual_cost_with_depreciation']]
        colors = px.colors.qualitative.Set3
        
        for i, category in enumerate(cost_categories):
            if category in df.columns:
                fig_line.add_trace(go.Scatter(
                x=df['ownership_year'] if 'ownership_year' in df.columns else list(range(1, len(df)+1)),  # FIXED
                y=df[category],
                mode='lines+markers',
                name=category.replace('_', ' ').title(),
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
                ))
        
        fig_line.update_layout(
            title="Annual Costs by Category",
            xaxis_title="Calendar Year",
            yaxis_title="Annual Cost ($)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Pie chart of total costs by category
        category_totals = results.get('category_totals', {})
        if category_totals:
            fig_pie = go.Figure(data=[go.Pie(
                labels=[cat.replace('_', ' ').title() for cat in category_totals.keys()],
                values=list(category_totals.values()),
                hole=0.3
            )])
            
            fig_pie.update_layout(
                title="Total Cost Distribution",
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)

def display_cost_breakdown(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display detailed cost breakdown - OPERATING COSTS ONLY with 15-year maximum bound"""
    
    st.subheader("💰 Annual Operating Cost Breakdown")
    st.info("💡 **Direct expenses only** - Depreciation tracked separately as opportunity cost")
    
    annual_breakdown = results.get('annual_breakdown', [])
    
    if annual_breakdown:
        # Get vehicle data
        current_mileage = vehicle_data.get('current_mileage', 0)
        annual_mileage = vehicle_data.get('annual_mileage', 12000)
        analysis_years = vehicle_data.get('analysis_years', 5)
        
        # BOUND THE ANALYSIS WINDOW: Maximum 15 years
        max_years = min(analysis_years, 15)
        
        # Limit the breakdown data to the bounded window
        bounded_breakdown = annual_breakdown[:max_years]
        
        st.write(f"Debug: Starting mileage = {current_mileage:,}, Annual mileage = {annual_mileage:,}")
        st.write(f"Debug: Analysis period bounded to {max_years} years (max 15)")
        
        # Create detailed breakdown table
        breakdown_data = []
        
        for year_index, year_data in enumerate(bounded_breakdown):
            year_of_ownership = year_index + 1
            
            # Ensure we don't exceed the bounded period
            if year_of_ownership > max_years:
                break
            
            # FIXED: Calculate correct total mileage including starting mileage
            calculated_total_mileage = current_mileage + (annual_mileage * year_of_ownership)
            
            # Use calculated mileage (always reliable)
            display_mileage = calculated_total_mileage
            
            # Calculate the year (from 2025 forward)
            ownership_year = 2025 + year_index
            
            row = {
                'Year': ownership_year,
                'Mileage': f"{display_mileage:,}",
            }
            
            # Add cost categories - REMOVE DEPRECIATION
            if vehicle_data.get('transaction_type', 'Purchase') == 'Purchase':
                row.update({
                    'Maintenance': f"${year_data.get('annual_maintenance', year_data.get('maintenance', 0)):,.0f}",
                    'Insurance': f"${year_data.get('annual_insurance', year_data.get('insurance', 0)):,.0f}",
                    'Fuel/Energy': f"${year_data.get('annual_energy', year_data.get('fuel_energy', 0)):,.0f}",
                    'Financing': f"${year_data.get('financing', 0):,.0f}",
                })
                
                # Calculate operating total
                maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 0))
                insurance = year_data.get('annual_insurance', year_data.get('insurance', 0))
                fuel_energy = year_data.get('annual_energy', year_data.get('fuel_energy', 0))
                financing = year_data.get('financing', 0)
                operating_total = maintenance + insurance + fuel_energy + financing
                
            else:  # Lease
                row.update({
                    'Lease Payment': f"${year_data.get('lease_payment', 0):,.0f}",
                    'Maintenance': f"${year_data.get('annual_maintenance', year_data.get('maintenance', 0)):,.0f}",
                    'Insurance': f"${year_data.get('annual_insurance', year_data.get('insurance', 0)):,.0f}",
                    'Fuel/Energy': f"${year_data.get('annual_energy', year_data.get('fuel_energy', 0)):,.0f}",
                    'Excess Fees': f"${year_data.get('excess_fees', 0):,.0f}",
                })
                
                # Calculate operating total
                lease_payment = year_data.get('lease_payment', 0)
                maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 0))
                insurance = year_data.get('annual_insurance', year_data.get('insurance', 0))
                fuel_energy = year_data.get('annual_energy', year_data.get('fuel_energy', 0))
                excess_fees = year_data.get('excess_fees', 0)
                operating_total = lease_payment + maintenance + insurance + fuel_energy + excess_fees
            
            row['Operating Total'] = f"${operating_total:,.0f}"
            breakdown_data.append(row)
        
        # Display the bounded table
        df_breakdown = pd.DataFrame(breakdown_data)
        st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
        
        # Add info about the analysis period
        if current_mileage > 0:
            final_mileage = current_mileage + (annual_mileage * max_years)
            st.info(f"📊 **Used Vehicle Analysis:** Starting at {current_mileage:,} miles, ending at {final_mileage:,} miles over {max_years} years")
        else:
            final_mileage = annual_mileage * max_years
            st.info(f"📊 **New Vehicle Analysis:** {final_mileage:,} total miles over {max_years} years")
        
        # Add depreciation summary separately (only for purchases)
        if vehicle_data.get('transaction_type', 'Purchase') == 'Purchase':
            st.markdown("---")
            st.subheader("📈 Depreciation Summary")
            st.info("💡 **Opportunity cost** - Not a direct annual expense")
            
            if bounded_breakdown:
                total_depreciation = sum(year_data.get('annual_depreciation', year_data.get('depreciation', 0)) for year_data in bounded_breakdown)
                st.metric("Total Depreciation", f"${total_depreciation:,.0f}", 
                         help=f"Total value loss over {max_years}-year period")


# Alternative: Even cleaner version that handles bounds in the calculation itself
def display_cost_breakdown_clean(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Clean version with built-in bounds and error handling"""
    
    st.subheader("💰 Annual Operating Cost Breakdown")
    st.info("💡 **Direct expenses only** - Depreciation tracked separately as opportunity cost")
    
    # Get vehicle data with defaults
    current_mileage = vehicle_data.get('current_mileage', 0)
    annual_mileage = vehicle_data.get('annual_mileage', 12000)
    analysis_years = vehicle_data.get('analysis_years', 5)
    transaction_type = vehicle_data.get('transaction_type', 'Purchase')
    
    # ENFORCE BOUNDS: 1-15 years maximum
    bounded_years = max(1, min(analysis_years, 15))
    
    annual_breakdown = results.get('annual_breakdown', [])
    
    # Create reliable breakdown data
    breakdown_data = []
    
    for year_num in range(1, bounded_years + 1):
        # Calculate reliable values
        ownership_year = 2024 + year_num  # 2025, 2026, etc.
        total_mileage = current_mileage + (annual_mileage * year_num)
        
        # Get data from breakdown if available, otherwise use defaults
        if year_num <= len(annual_breakdown):
            year_data = annual_breakdown[year_num - 1]
        else:
            # Create default data if breakdown is incomplete
            year_data = {
                'annual_maintenance': 500 + (year_num * 100),  # Increasing maintenance
                'annual_insurance': 1200,  # Stable insurance
                'annual_energy': 2500,     # Default fuel/energy
                'financing': 0,            # Default no financing
                'annual_depreciation': 0   # Default no depreciation
            }
        
        row = {
            'Year': ownership_year,
            'Mileage': f"{total_mileage:,}",
        }
        
        # Add cost categories based on transaction type
        if transaction_type == 'Purchase':
            maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 500))
            insurance = year_data.get('annual_insurance', year_data.get('insurance', 1200))
            fuel_energy = year_data.get('annual_energy', year_data.get('fuel_energy', 2500))
            financing = year_data.get('financing', 0)
            
            row.update({
                'Maintenance': f"${maintenance:,.0f}",
                'Insurance': f"${insurance:,.0f}",
                'Fuel/Energy': f"${fuel_energy:,.0f}",
                'Financing': f"${financing:,.0f}",
            })
            
            operating_total = maintenance + insurance + fuel_energy + financing
            
        else:  # Lease
            lease_payment = year_data.get('lease_payment', 400)
            maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 200))
            insurance = year_data.get('annual_insurance', year_data.get('insurance', 1200))
            fuel_energy = year_data.get('annual_energy', year_data.get('fuel_energy', 2500))
            excess_fees = year_data.get('excess_fees', 0)
            
            row.update({
                'Lease Payment': f"${lease_payment:,.0f}",
                'Maintenance': f"${maintenance:,.0f}",
                'Insurance': f"${insurance:,.0f}",
                'Fuel/Energy': f"${fuel_energy:,.0f}",
                'Excess Fees': f"${excess_fees:,.0f}",
            })
            
            operating_total = lease_payment + maintenance + insurance + fuel_energy + excess_fees
        
        row['Operating Total'] = f"${operating_total:,.0f}"
        breakdown_data.append(row)
    
    # Display table
    df_breakdown = pd.DataFrame(breakdown_data)
    st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
    
    # Summary info
    final_mileage = current_mileage + (annual_mileage * bounded_years)
    st.success(f"✅ **Analysis Period:** {bounded_years} years | **Mileage:** {current_mileage:,} → {final_mileage:,} miles")
    
    # Depreciation summary for purchases
    if transaction_type == 'Purchase' and annual_breakdown:
        st.markdown("---")
        st.subheader("📈 Depreciation Summary")
        st.info("💡 **Opportunity cost** - Not a direct annual expense")
        
        # Only sum depreciation for the bounded period
        bounded_depreciation = sum(
            annual_breakdown[i].get('annual_depreciation', annual_breakdown[i].get('depreciation', 0)) 
            for i in range(min(bounded_years, len(annual_breakdown)))
        )
        st.metric("Total Depreciation", f"${bounded_depreciation:,.0f}", 
                 help=f"Total value loss over {bounded_years}-year period")

def display_recommendations_tab(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display recommendations and insights"""
    
    st.subheader("🎯 Recommendations & Insights")
    
    # Affordability assessment
    affordability = results.get('affordability', {})
    
    if affordability:
        income_percentage = affordability.get('percentage_of_income', 0)
        is_affordable = affordability.get('is_affordable', False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if is_affordable:
                st.success(f"✅ **Budget Friendly**")
                st.write(f"This vehicle represents {income_percentage:.1f}% of your income, which is within recommended guidelines.")
            else:
                st.warning(f"⚠️ **Budget Consideration**")
                st.write(f"This vehicle represents {income_percentage:.1f}% of your income, which may strain your budget.")
        
        with col2:
            monthly_impact = affordability.get('monthly_budget_impact', 0)
            st.metric("Monthly Budget Impact", f"${monthly_impact:,.0f}")
    
    # Cost optimization suggestions
    st.markdown("#### 💰 Cost Optimization Tips")
    
    suggestions = []
    
    # Generic suggestions based on transaction type
    if vehicle_data.get('transaction_type') == 'Purchase':
        suggestions.extend([
            "🔧 **Maintenance**: Use independent shops for routine maintenance to save 20-30%",
            "⛽ **Fuel**: Consider fuel-efficient driving techniques to improve MPG by 10-15%",
            "🛡️ **Insurance**: Shop around annually - savings of $200-500 possible",
            "📅 **Timing**: Proper maintenance timing can prevent costly repairs"
        ])
    else:  # Lease
        suggestions.extend([
            "📏 **Mileage**: Monitor mileage closely to avoid overage fees",
            "🔧 **Maintenance**: Keep all service records for lease return",
            "🛡️ **Protection**: Consider gap insurance for lease coverage",
            "⏰ **Early Return**: Understand early termination costs before making changes"
        ])
    
    for suggestion in suggestions:
        st.markdown(suggestion)
    
    # Comparison recommendation
    st.markdown("#### 🔄 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Consider Comparing:**")
        st.write("• Similar vehicles from other manufacturers")
        st.write("• Different trim levels of the same model")
        st.write("• Lease vs purchase for this vehicle")
    
    with col2:
        st.markdown("**Before You Decide:**")
        st.write("• Test drive the vehicle")
        st.write("• Get insurance quotes")
        st.write("• Negotiate purchase/lease terms")
        st.write("• Consider certified pre-owned options")
    
    # MOVED: Add to comparison button - now at the bottom of recommendations tab
    st.markdown("---")
    st.markdown("#### 🔄 Vehicle Comparison")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Compare this vehicle** with other options to make the best decision:")
    
    with col2:
        if st.button("➕ Add to Comparison", type="primary", use_container_width=True, key="add_to_comparison_recommendations"):
            try:
                vehicle_data = st.session_state.current_vehicle
                success, message = add_vehicle_to_comparison(vehicle_data)
                if success:
                    st.success("✅ " + message)
                    st.info("Go to 'Multi-Vehicle Comparison' to compare with other vehicles.")
                else:
                    st.warning("⚠️ " + message)
            except Exception as e:
                st.error(f"Error adding to comparison: {str(e)}")