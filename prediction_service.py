"""
Main Prediction Service
Orchestrates all TCO calculations and coordinates between different models
Enhanced with detailed maintenance scheduling
"""

from typing import Dict, Any, List
import math

from models.depreciation.enhanced_depreciation import EnhancedDepreciationModel
from models.maintenance.maintenance_utils import MaintenanceCalculator
from models.insurance.advanced_insurance import AdvancedInsuranceCalculator
from models.fuel.fuel_utils import FuelCostCalculator
from models.fuel.electric_vehicle_utils import EVCostCalculator
from services.financial_analysis import FinancialAnalysisService
from data.vehicle_database import get_vehicle_characteristics
from utils.zip_code_utils import get_regional_cost_multiplier

class PredictionService:
    """Main service for orchestrating TCO predictions"""
    
    def __init__(self):
        self.depreciation_model = EnhancedDepreciationModel()
        self.maintenance_calculator = MaintenanceCalculator()
        self.insurance_calculator = AdvancedInsuranceCalculator()
        self.fuel_calculator = FuelCostCalculator()
        self.ev_calculator = EVCostCalculator()
        self.financial_service = FinancialAnalysisService()
    
    def calculate_total_cost_of_ownership(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive TCO with proper cost separation
        FIXED: Returns corrected cost structure with out-of-pocket vs TCO separation
        """
        
        # Get vehicle characteristics
        vehicle_characteristics = get_vehicle_characteristics(
            input_data['make'], 
            input_data['model'], 
            input_data['year']
        )
        
        # Get regional cost adjustments
        regional_multiplier = get_regional_cost_multiplier(
            input_data.get('zip_code', ''),
            input_data.get('state', '')
        )
        
        analysis_years = input_data.get('analysis_years', 5)
        
        # Route to appropriate calculation method
        if input_data.get('transaction_type', 'purchase').lower() == 'lease':
            return self._calculate_lease_tco(input_data, vehicle_characteristics, regional_multiplier)
        else:
            return self._calculate_purchase_tco(input_data, vehicle_characteristics, regional_multiplier)
    
    def _calculate_realistic_used_vehicle_depreciation(self, input_data: Dict[str, Any], 
                                                    initial_value: float, 
                                                    analysis_years: int) -> List[Dict[str, Any]]:
        """Calculate realistic depreciation for used vehicles starting from current value"""
        
        from datetime import datetime
        current_year = datetime.now().year
        vehicle_age_at_purchase = current_year - input_data['year']
        
        # Used vehicles depreciate differently than new vehicles
        # They follow a more gradual, linear depreciation pattern
        
        schedule = []
        current_value = initial_value  # Start with actual purchase price, not original MSRP
        
        # Used vehicle depreciation rates (much lower than new vehicles)
        if vehicle_age_at_purchase <= 3:
            # Recently used (1-3 years) - still depreciates moderately
            annual_rates = [0.08, 0.07, 0.06, 0.05, 0.04]  # 8%, 7%, 6%, 5%, 4%
        elif vehicle_age_at_purchase <= 7:
            # Mid-age used (4-7 years) - slower depreciation
            annual_rates = [0.05, 0.04, 0.04, 0.03, 0.03]  # 5%, 4%, 4%, 3%, 3%
        else:
            # Older used (8+ years) - minimal depreciation
            annual_rates = [0.03, 0.02, 0.02, 0.02, 0.02]  # 3%, 2%, 2%, 2%, 2%
        
        # Apply brand multipliers
        brand_multipliers = {
            'Toyota': 0.8, 'Honda': 0.8, 'Lexus': 0.7,  # Better retention
            'BMW': 1.2, 'Mercedes-Benz': 1.2, 'Audi': 1.1,  # Faster depreciation
            'Chevrolet': 1.0, 'Ford': 1.0, 'Hyundai': 0.9
        }
        brand_multiplier = brand_multipliers.get(input_data['make'], 1.0)
        
        for year in range(1, analysis_years + 1):
            # Use flatter depreciation curve for used vehicles
            base_rate = annual_rates[min(year - 1, len(annual_rates) - 1)]
            adjusted_rate = base_rate * brand_multiplier
            
            # Calculate depreciation for this year
            annual_depreciation = current_value * adjusted_rate
            new_value = current_value - annual_depreciation
            
            # Ensure minimum value (used vehicles retain some value)
            min_value = initial_value * 0.15  # Minimum 15% of purchase price
            new_value = max(new_value, min_value)
            annual_depreciation = current_value - new_value  # Recalculate if min value applied
            
            ownership_year = current_year + year - 1
            
            schedule.append({
                'year': year,
                'ownership_year': ownership_year,
                'vehicle_age': ownership_year - input_data['year'],
                'vehicle_value': new_value,
                'annual_depreciation': annual_depreciation,
                'depreciation_rate': adjusted_rate
            })
            
            current_value = new_value
        
        return schedule

    def _calculate_purchase_tco(self, input_data: Dict[str, Any], 
                                            vehicle_characteristics: Dict[str, Any], 
                                            regional_multiplier: float) -> Dict[str, Any]:
            """
            Calculate comprehensive purchase TCO with corrected cost separation
            FIXED: Properly separates out-of-pocket costs from total TCO
            """
            
            analysis_years = input_data.get('analysis_years', 5)
            purchase_price = input_data.get('price', input_data.get('trim_msrp', 25000))
            current_mileage = input_data.get('current_mileage', 0)
            
            # Initialize category totals
            category_totals = {
                'depreciation': 0,
                'maintenance': 0,
                'insurance': 0,
                'fuel_energy': 0,
                'financing': 0
            }
            
            annual_breakdown = []
          
            # Check if this is a used vehicle with smarter logic for current model year
            from datetime import datetime
            current_year = datetime.now().year
            vehicle_age_at_purchase = current_year - input_data['year']

            # IMPROVED: Smarter used vehicle detection
            if vehicle_age_at_purchase > 0:
                # Truly older vehicle - always use used vehicle logic
                is_used_vehicle = True
            elif vehicle_age_at_purchase == 0 and current_mileage > 3000:
                # Current year but very high mileage - treat as used
                is_used_vehicle = True
            else:
                # Current year with reasonable mileage - treat as new with mileage adjustment
                is_used_vehicle = False
            
            # FIXED: Use appropriate depreciation calculation for used vs new vehicles
            if is_used_vehicle:
                # For used vehicles, use realistic used vehicle depreciation rates
                depreciation_schedule = self._calculate_realistic_used_vehicle_depreciation(
                    input_data=input_data,
                    initial_value=purchase_price,  # Start from purchase price, not MSRP
                    analysis_years=analysis_years
                )
            else:
                # For new vehicles, use the enhanced model
                depreciation_schedule = self.depreciation_model.calculate_depreciation_schedule(
                    purchase_price,                      # initial_value (positional)
                    input_data['make'],                  # vehicle_make (positional)
                    input_data['model'],                 # vehicle_model (positional)
                    input_data['year'],                  # model_year (positional)
                    input_data['annual_mileage'],        # annual_mileage (positional)
                    analysis_years                       # years (positional)
                )
            
            # Calculate financing schedule if needed
            financing_schedule = None
            if (input_data.get('financing_type', 'cash') != 'cash' or 
                input_data.get('loan_amount', 0) > 0 or 
                input_data.get('financing_option') == 'finance'):
                
                loan_amount = input_data.get('loan_amount', purchase_price * 0.8)
                if loan_amount > 0:
                    financing_schedule = self.financial_service.calculate_loan_payments(
                        loan_amount=loan_amount,
                        interest_rate=input_data.get('interest_rate', 5.0),
                        loan_term_years=input_data.get('loan_term', 5),
                        analysis_years=analysis_years
                    )
            
            # Calculate maintenance schedule
            base_maintenance_schedule = self.maintenance_calculator.get_maintenance_schedule(
                annual_mileage=input_data['annual_mileage'],
                years=analysis_years,
                starting_mileage=current_mileage,
                vehicle_make=input_data['make'],
                driving_style=input_data.get('driving_style', 'normal'),
                vehicle_model=input_data['model']
            )
            
            adjusted_maintenance_schedule = self._adjust_maintenance_schedule(
                base_maintenance_schedule,
                input_data['make'],
                input_data.get('shop_type', 'independent'),
                regional_multiplier
            )
            
            # Calculate costs for each year
            for year in range(1, analysis_years + 1):
                ownership_year = 2024 + year
                
                # Depreciation (from schedule)
                annual_depreciation = 0
                if year <= len(depreciation_schedule):
                    if year == 1:
                        annual_depreciation = purchase_price - depreciation_schedule[year-1]['vehicle_value']
                    else:
                        annual_depreciation = depreciation_schedule[year-2]['vehicle_value'] - depreciation_schedule[year-1]['vehicle_value']
                
                # Maintenance (from adjusted schedule)
                annual_maintenance = 0
                maintenance_activities = []
                if year <= len(adjusted_maintenance_schedule):
                    annual_maintenance = adjusted_maintenance_schedule[year-1]['total_year_cost']
                    maintenance_activities = adjusted_maintenance_schedule[year-1].get('services', [])
                
                # Insurance
                annual_insurance = self.insurance_calculator.calculate_annual_premium(
                    vehicle_value=depreciation_schedule[year-1]['vehicle_value'] if year <= len(depreciation_schedule) else purchase_price * 0.5,
                    vehicle_make=input_data['make'],
                    vehicle_year=input_data['year'],
                    driver_age=input_data.get('driver_age', 35),
                    state=input_data['state'],
                    coverage_type=input_data.get('coverage_type', 'comprehensive'),
                    annual_mileage=input_data['annual_mileage'],
                    num_vehicles=input_data.get('num_household_vehicles', 2),
                    regional_multiplier=regional_multiplier,
                    vehicle_model=input_data['model']
                )
                
                # Fuel/Energy costs
                if input_data.get('is_electric', False):
                    annual_fuel = self.ev_calculator.calculate_annual_electricity_cost(
                        annual_mileage=input_data['annual_mileage'],
                        vehicle_efficiency=vehicle_characteristics.get('efficiency', 32),
                        electricity_rate=input_data.get('electricity_rate', 0.12),
                        charging_preference=input_data.get('charging_preference', 'mixed')
                    )
                else:
                    annual_fuel = self.fuel_calculator.calculate_annual_fuel_cost(
                        annual_mileage=input_data['annual_mileage'],
                        mpg=vehicle_characteristics.get('mpg', 25),
                        fuel_price=input_data.get('fuel_price', 3.50),
                        driving_style=input_data.get('driving_style', 'normal'),
                        terrain=input_data.get('terrain', 'mixed')
                    )
                
                # Financing costs
                annual_financing = 0
                if financing_schedule and year <= len(financing_schedule):
                    annual_financing = financing_schedule[year-1].get('annual_payment', 0)
                
                # Total annual cost
                total_annual = annual_depreciation + annual_maintenance + annual_insurance + annual_fuel + annual_financing
                
                # Store breakdown with correct ownership years
                annual_breakdown.append({
                    'year': year,
                    'ownership_year': ownership_year,
                    'vehicle_age': ownership_year - input_data['year'],
                    'vehicle_model_year': input_data['year'],
                    'cumulative_mileage': current_mileage + (input_data['annual_mileage'] * year),
                    'depreciation': annual_depreciation,
                    'maintenance': annual_maintenance,
                    'maintenance_activities': maintenance_activities,
                    'insurance': annual_insurance,
                    'fuel_energy': annual_fuel,
                    'financing': annual_financing,
                    'total_annual_cost': total_annual
                })
                
                # Add to totals
                category_totals['depreciation'] += annual_depreciation
                category_totals['maintenance'] += annual_maintenance
                category_totals['insurance'] += annual_insurance
                category_totals['fuel_energy'] += annual_fuel
                category_totals['financing'] += annual_financing
            
            # Calculate final metrics with proper cost separation
            total_tco = sum(category_totals.values())
            
            # FIXED: Separate out-of-pocket costs (exclude depreciation)
            out_of_pocket_total = (
                category_totals['maintenance'] +
                category_totals['insurance'] +
                category_totals['fuel_energy'] +
                category_totals['financing']
            )
            
            average_annual_tco = total_tco / analysis_years
            average_annual_out_of_pocket = out_of_pocket_total / analysis_years
            
            total_miles = input_data['annual_mileage'] * analysis_years
            cost_per_mile_out_of_pocket = out_of_pocket_total / total_miles if total_miles > 0 else 0
            cost_per_mile_tco = total_tco / total_miles if total_miles > 0 else 0
            
            final_vehicle_value = depreciation_schedule[-1]['vehicle_value'] if depreciation_schedule else purchase_price * 0.15
            
            return {
                'summary': {
                    # FIXED: Ensure primary metrics are ALWAYS out-of-pocket costs
                    'total_ownership_cost': out_of_pocket_total,  # This should be the main "total cost"
                    'average_annual_cost': average_annual_out_of_pocket,  
                    'cost_per_mile': cost_per_mile_out_of_pocket,  
                    'final_vehicle_value': final_vehicle_value,
                    'total_depreciation': category_totals['depreciation'],
                    'purchase_price': purchase_price,
                    'original_msrp': input_data.get('trim_msrp', purchase_price),
                    'is_used_vehicle': current_mileage > 0,
                    
                    # Additional TCO metrics for reference only
                    'total_tco_with_depreciation': total_tco,  # Complete TCO including depreciation
                    'average_annual_tco': average_annual_tco,  
                    'cost_per_mile_tco': cost_per_mile_tco,  
                    'out_of_pocket_total': out_of_pocket_total  # Explicit out-of-pocket total
                },
                'annual_breakdown': annual_breakdown,
                'category_totals': category_totals,
                'depreciation_schedule': depreciation_schedule,
                'financing_schedule': financing_schedule,
                'maintenance_schedule': adjusted_maintenance_schedule,
                'affordability': self._calculate_affordability(
                    annual_cost=average_annual_out_of_pocket,  
                    gross_income=input_data.get('gross_income', 60000),
                    transaction_type='purchase'
                ),
                'vehicle_characteristics': vehicle_characteristics,
                'assumptions': self._get_calculation_assumptions(input_data, vehicle_characteristics),
                # FIXED: Add explicit out-of-pocket calculation for display
                'display_total_cost': out_of_pocket_total,  # Explicit field for display
                'display_includes_depreciation': False  # Flag to indicate this excludes depreciation
            }

    def _adjust_maintenance_schedule(self, base_schedule: List[Dict[str, Any]], 
                                vehicle_make: str, shop_type: str, 
                                regional_multiplier: float) -> List[Dict[str, Any]]:
        """Apply brand, shop, and regional adjustments to maintenance schedule - FIXED"""
        
        # FIXED: Reduce multiplier impact since enhanced maintenance_utils already has realistic costs
        brand_multiplier = self.maintenance_calculator.brand_multipliers.get(vehicle_make, 1.0)
        
        # FIXED: Reduce shop multiplier impact - the base costs are already reasonable
        shop_multipliers = {
            'dealership': 1.15,      # REDUCED from 1.3 to 1.15 (15% premium)
            'independent': 1.0,      # Baseline
            'chain': 1.05,          # REDUCED from 1.1 to 1.05 (5% premium)  
            'specialty': 1.1,       # REDUCED from 1.2 to 1.1 (10% premium)
            'diy': 0.5             # Parts only
        }
        shop_multiplier = shop_multipliers.get(shop_type, 1.0)
        
        # FIXED: Cap regional multiplier to prevent excessive inflation
        regional_multiplier = max(0.8, min(1.3, regional_multiplier))
        
        adjusted_schedule = []
        
        for year_data in base_schedule:
            adjusted_services = []
            adjusted_total_cost = 0
            
            for service in year_data['services']:
                # FIXED: Apply reasonable multipliers instead of excessive ones
                base_cost = service['cost_per_service']
                
                # Apply brand adjustment (smaller impact)
                if brand_multiplier < 0.95:
                    # Reliable brands get small discount
                    adjusted_cost = base_cost * brand_multiplier
                elif brand_multiplier > 1.25:
                    # Luxury brands get moderate premium
                    adjusted_cost = base_cost * min(brand_multiplier, 1.4)  # Cap at 40% premium
                else:
                    # Most brands get minimal adjustment
                    adjusted_cost = base_cost * brand_multiplier
                
                # Apply shop and regional adjustments
                final_cost_per_service = adjusted_cost * shop_multiplier * regional_multiplier
                
                total_cost_for_service = final_cost_per_service * service['frequency']
                
                adjusted_services.append({
                    'service': service['service'],
                    'frequency': service['frequency'],
                    'cost_per_service': final_cost_per_service,
                    'total_cost': total_cost_for_service,
                    'shop_type': shop_type,
                    'interval_based': True
                })
                
                adjusted_total_cost += total_cost_for_service
            
            # FIXED: Reduce wear-based maintenance - the enhanced system already includes wear items
            vehicle_age = year_data['year']
            if vehicle_age > 3:
                # REDUCED wear cost since enhanced maintenance_utils includes detailed wear items
                wear_cost = self._calculate_year_specific_wear_maintenance(
                    vehicle_age, vehicle_make, shop_type, regional_multiplier
                )
                
                # FIXED: Only add wear cost if it's meaningful and not already covered
                if wear_cost > 100:  # Only add if significant
                    adjusted_services.append({
                        'service': 'Additional Wear & Tear',
                        'frequency': 1,
                        'cost_per_service': wear_cost,
                        'total_cost': wear_cost,
                        'shop_type': shop_type,
                        'interval_based': False
                    })
                    adjusted_total_cost += wear_cost
            
            adjusted_schedule.append({
                'year': year_data['year'],
                'total_mileage': year_data['total_mileage'],
                'starting_year_mileage': year_data.get('starting_year_mileage', 0),
                'ending_year_mileage': year_data.get('ending_year_mileage', 0),
                'services': adjusted_services,
                'total_year_cost': adjusted_total_cost,
                'brand_multiplier': brand_multiplier,
                'shop_multiplier': shop_multiplier,
                'regional_multiplier': regional_multiplier
            })
        
        return adjusted_schedule

    def _calculate_year_specific_wear_maintenance(self, vehicle_age: int, vehicle_make: str, 
                                                shop_type: str, regional_multiplier: float) -> float:
        """Calculate wear-based maintenance for a specific year - FIXED to reduce double-counting"""
        
        # FIXED: Reduced base wear costs since enhanced maintenance_utils includes detailed wear items
        base_wear_costs = {
            4: 100,   # REDUCED from 200 - Year 4: Minor additional repairs
            5: 150,   # REDUCED from 350 - Year 5: Some additional issues  
            6: 200,   # REDUCED from 500 - Year 6: Moderate additional wear
            7: 300,   # REDUCED from 750 - Year 7: Some additional repairs
            8: 400,   # REDUCED from 1000 - Year 8: More additional repairs
            9: 500,   # REDUCED from 1250 - Year 9: Increased maintenance
            10: 600   # REDUCED from 1500 - Year 10+: Higher maintenance
        }
        
        base_cost = base_wear_costs.get(min(vehicle_age, 10), 600)
        
        # Apply moderate multipliers
        brand_multiplier = self.maintenance_calculator.brand_multipliers.get(vehicle_make, 1.0)
        
        shop_multipliers = {
            'dealership': 1.15,
            'independent': 1.0,
            'chain': 1.05,
            'specialty': 1.1
        }
        shop_multiplier = shop_multipliers.get(shop_type, 1.0)
        
        # FIXED: Calculate reasonable wear cost
        wear_cost = base_cost * brand_multiplier * shop_multiplier * regional_multiplier
        
        return wear_cost
    
    def _calculate_lease_tco(self, input_data: Dict[str, Any], 
                            vehicle_characteristics: Dict[str, Any], 
                            regional_multiplier: float) -> Dict[str, Any]:
        """Calculate TCO for vehicle lease with starting mileage support"""
        
        lease_term = input_data['analysis_years']
        monthly_payment = input_data['lease_monthly_payment']
        annual_mileage_limit = input_data['lease_mileage_limit']
        down_payment = input_data.get('down_payment', 0)
        
        # FIXED: Calculate maintenance schedule for lease with starting mileage
        starting_mileage = input_data.get('current_mileage', 0)  # Even leases can be used vehicles
        
        base_maintenance_schedule = self.maintenance_calculator.get_maintenance_schedule(
            annual_mileage=annual_mileage_limit,
            years=lease_term,
            starting_mileage=starting_mileage  # FIXED: Pass starting mileage
        )
        
        # Apply lease-specific adjustments (warranty coverage)
        lease_maintenance_schedule = self._adjust_lease_maintenance_schedule(
            base_maintenance_schedule,
            input_data['make'],
            regional_multiplier
        )
        
        annual_breakdown = []
        category_totals = {
            'lease_payments': 0,
            'maintenance': 0,
            'insurance': 0,
            'fuel_energy': 0,
            'fees_penalties': 0
        }
        
        # Calculate year-by-year costs
        from datetime import datetime
        lease_start_year = datetime.now().year  # 2025 - when the lease starts
        
        # Calculate year-by-year costs
        for year in range(1, lease_term + 1):
            ownership_year = lease_start_year + year - 1  # CORRECT: 2025, 2026, 2027, etc.
            current_mileage = annual_mileage_limit * year
            
            # Lease payments (12 months)
            annual_lease_payment = monthly_payment * 12
            
            # Maintenance (with detailed activities)
            if year <= len(lease_maintenance_schedule):
                annual_maintenance = lease_maintenance_schedule[year-1]['total_year_cost']
                maintenance_activities = lease_maintenance_schedule[year-1]['services']
            else:
                annual_maintenance = 0
                maintenance_activities = []
            
            # Insurance (required for leased vehicles)
            vehicle_value = input_data['trim_msrp']  # Use MSRP for lease insurance
            annual_insurance = self.insurance_calculator.calculate_annual_premium(
                vehicle_value=vehicle_value,
                vehicle_make=input_data['make'],
                vehicle_year=input_data['year'],
                driver_age=input_data['user_age'],
                state=input_data['state'],
                coverage_type='comprehensive',  # Required for leases
                annual_mileage=annual_mileage_limit,
                num_vehicles=input_data['num_household_vehicles'],
                regional_multiplier=regional_multiplier
            )
            
            # Fuel/Energy costs (limited by lease mileage)
            if vehicle_characteristics.get('is_electric', False):
                annual_fuel = self.ev_calculator.calculate_annual_electricity_cost(
                    annual_mileage=annual_mileage_limit,
                    vehicle_efficiency=vehicle_characteristics.get('mpge', 100),
                    electricity_rate=input_data.get('electricity_rate', 0.12),
                    charging_preference=input_data.get('charging_pref', 'mixed')
                )
            else:
                annual_fuel = self.fuel_calculator.calculate_annual_fuel_cost(
                    annual_mileage=annual_mileage_limit,
                    mpg=vehicle_characteristics.get('mpg', 25),
                    fuel_price=input_data['fuel_price'],
                    driving_style=input_data['driving_style'],
                    terrain=input_data['terrain']
                )
            
            # Calculate any fees or penalties (mileage overage, wear and tear)
            annual_fees = self._calculate_lease_fees_and_penalties(
                actual_mileage=input_data.get('annual_mileage', annual_mileage_limit),
                allowed_mileage=annual_mileage_limit,
                lease_year=year,
                vehicle_value=vehicle_value
            )
            
            # Total annual cost
            total_annual = annual_lease_payment + annual_maintenance + annual_insurance + annual_fuel + annual_fees
            
            # FIXED: Store breakdown with correct ownership years
            annual_breakdown.append({
                'year': year,  # Lease year (1, 2, 3, etc.)
                'ownership_year': ownership_year,  # CORRECT: Calendar year (2025, 2026, 2027, etc.)
                'lease_year': year,  # Same as year, kept for compatibility
                'vehicle_age': ownership_year - input_data['year'],  # CORRECT: Actual vehicle age
                'vehicle_model_year': input_data['year'],  # Original model year
                'lease_payment': annual_lease_payment,
                'maintenance': annual_maintenance,
                'maintenance_activities': maintenance_activities,
                'cumulative_mileage': current_mileage,
                'insurance': annual_insurance,
                'fuel_energy': annual_fuel,
                'fees_penalties': annual_fees,
                'total_annual_cost': total_annual
            })
            
            # Add to category totals
            category_totals['lease_payments'] += annual_lease_payment
            category_totals['maintenance'] += annual_maintenance
            category_totals['insurance'] += annual_insurance
            category_totals['fuel_energy'] += annual_fuel
            category_totals['fees_penalties'] += annual_fees
        
        # Calculate summary metrics
        total_lease_cost = sum(category_totals.values()) + down_payment
        average_annual_cost = total_lease_cost / lease_term
        average_monthly_cost = total_lease_cost / (lease_term * 12)
        total_miles = annual_mileage_limit * lease_term
        cost_per_mile = total_lease_cost / total_miles if total_miles > 0 else 0
        
        # Calculate affordability
        affordability = self._calculate_affordability(
            annual_cost=average_annual_cost,
            gross_income=input_data['gross_income'],
            transaction_type='lease'
        )
        
        return {
            'summary': {
                'total_lease_cost': total_lease_cost,
                'average_annual_cost': average_annual_cost,
                'average_monthly_cost': average_monthly_cost,
                'cost_per_mile': cost_per_mile,
                'down_payment': down_payment
            },
            'annual_breakdown': annual_breakdown,
            'category_totals': category_totals,
            'maintenance_schedule': lease_maintenance_schedule,  # NEW: Include detailed schedule
            'affordability': affordability,
            'vehicle_characteristics': vehicle_characteristics,
            'assumptions': self._get_calculation_assumptions(input_data, vehicle_characteristics)
        }
    
    def _adjust_lease_maintenance_schedule(self, base_schedule: List[Dict[str, Any]], 
                                         vehicle_make: str, regional_multiplier: float) -> List[Dict[str, Any]]:
        """Apply lease-specific adjustments to maintenance schedule (warranty coverage)"""
        
        brand_multiplier = self.maintenance_calculator.brand_multipliers.get(vehicle_make, 1.0)
        shop_multiplier = 1.2  # Dealership service for leases
        
        adjusted_schedule = []
        
        for year_data in base_schedule:
            lease_year = year_data['year']
            adjusted_services = []
            adjusted_total_cost = 0
            
            # Apply warranty discounts based on lease year
            if lease_year <= 2:
                warranty_discount = 0.6  # 60% covered by warranty
            elif lease_year <= 3:
                warranty_discount = 0.4  # 40% covered by warranty
            else:
                warranty_discount = 0.2  # 20% covered by extended warranty
            
            for service in year_data['services']:
                # Apply multipliers and warranty discount
                full_cost = (service['cost_per_service'] * 
                           brand_multiplier * 
                           shop_multiplier * 
                           regional_multiplier)
                
                out_of_pocket_cost = full_cost * (1 - warranty_discount)
                
                if out_of_pocket_cost > 5:  # Only include if cost is meaningful
                    adjusted_services.append({
                        'service': service['service'],
                        'frequency': service['frequency'],
                        'cost_per_service': out_of_pocket_cost,
                        'total_cost': out_of_pocket_cost * service['frequency'],
                        'warranty_covered': full_cost * warranty_discount * service['frequency'],
                        'shop_type': 'dealership',
                        'interval_based': True
                    })
                    adjusted_total_cost += out_of_pocket_cost * service['frequency']
            
            # Lease vehicles rarely need wear repairs in first few years
            if lease_year > 3:
                wear_cost = 100 * brand_multiplier * regional_multiplier  # Minimal wear
                adjusted_services.append({
                    'service': 'Minor Wear Items',
                    'frequency': 1,
                    'cost_per_service': wear_cost,
                    'total_cost': wear_cost,
                    'warranty_covered': 0,
                    'shop_type': 'dealership',
                    'interval_based': False
                })
                adjusted_total_cost += wear_cost
            
            adjusted_schedule.append({
                'year': lease_year,
                'total_mileage': year_data['total_mileage'],
                'services': adjusted_services,
                'total_year_cost': adjusted_total_cost,
                'warranty_discount': warranty_discount,
                'brand_multiplier': brand_multiplier,
                'shop_multiplier': shop_multiplier,
                'regional_multiplier': regional_multiplier
            })
        
        return adjusted_schedule
    
    def _calculate_lease_fees_and_penalties(self, actual_mileage: int, allowed_mileage: int, 
                                          lease_year: int, vehicle_value: float) -> float:
        """Calculate potential lease fees and penalties"""
        fees = 0
        
        # Mileage overage penalty (typically $0.15-0.30 per mile)
        if actual_mileage > allowed_mileage:
            overage_miles = actual_mileage - allowed_mileage
            overage_rate = 0.20  # $0.20 per mile default
            fees += overage_miles * overage_rate
        
        # Wear and tear estimate (small amount annually)
        wear_tear_rate = vehicle_value * 0.001  # 0.1% of vehicle value
        fees += wear_tear_rate
        
        return fees
    
    def _calculate_affordability(self, annual_cost: float, gross_income: float, 
                               transaction_type: str) -> Dict[str, Any]:
        """Calculate affordability metrics"""
        
        monthly_cost = annual_cost / 12
        percentage_of_income = (annual_cost / gross_income) * 100
        
        # Updated affordability threshold: 10% or less for both lease and purchase
        recommended_max = 10  # 10% of income for both leases and purchases
        
        is_affordable = percentage_of_income <= recommended_max
        
        return {
            'annual_cost': annual_cost,
            'monthly_cost': monthly_cost,
            'percentage_of_income': percentage_of_income,
            'is_affordable': is_affordable,
            'recommended_max_percentage': recommended_max,
            'monthly_budget_impact': monthly_cost,
            'affordability_score': min(100, (recommended_max / percentage_of_income) * 100) if percentage_of_income > 0 else 100
        }
    
    def _get_calculation_assumptions(self, input_data: Dict[str, Any], 
                                   vehicle_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Get assumptions used in calculations"""
        
        return {
            'depreciation_method': 'Enhanced market-based model',
            'maintenance_source': 'Manufacturer schedules + historical data',
            'insurance_basis': 'State-specific rates with driver profile',
            'fuel_prices': 'Current regional averages',
            'regional_adjustments': f"{input_data['geography_type']} geography in {input_data['state']}",
            'reliability_score': vehicle_characteristics.get('reliability_score', 3.5),
            'market_segment': vehicle_characteristics.get('market_segment', 'standard'),
            'calculation_date': '2025-08-08',
            'data_sources': [
                'Manufacturer MSRP data',
                'Regional fuel price databases', 
                'State insurance regulations',
                'Historical depreciation curves'
            ]
        }
    def _update_results_structure_for_display(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update results structure to match display expectations
        FIXED: Ensures proper cost separation for display functions
        """
        
        summary = results.get('summary', {})
        category_totals = results.get('category_totals', {})
        
        # Calculate out-of-pocket costs (excluding depreciation)
        out_of_pocket_total = (
            category_totals.get('maintenance', 0) +
            category_totals.get('insurance', 0) +
            category_totals.get('fuel_energy', 0) +
            category_totals.get('financing', 0)
        )
        
        # Update results structure for backward compatibility with display code
        display_results = results.copy()
        display_results.update({
            'total_cost': out_of_pocket_total,  # Main "total cost" is now out-of-pocket only
            'annual_cost': summary.get('average_annual_cost', 0),  # Already based on out-of-pocket
            'cost_per_mile': summary.get('cost_per_mile', 0),  # Already based on out-of-pocket
            'final_value': summary.get('final_vehicle_value', 0),
            'depreciation': category_totals.get('depreciation', 0),
            'maintenance': category_totals.get('maintenance', 0),
            'insurance': category_totals.get('insurance', 0),
            'energy': category_totals.get('fuel_energy', 0),
            'financing': category_totals.get('financing', 0),
            'total_tco': summary.get('total_tco', out_of_pocket_total + category_totals.get('depreciation', 0)),  # Complete TCO for reference
            'annual_operating_cost': out_of_pocket_total,  # For compatibility
            'is_electric': results.get('vehicle_characteristics', {}).get('is_electric', False)
        })
        
        return display_results