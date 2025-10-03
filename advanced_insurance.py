"""
Advanced Insurance Calculator
Calculates insurance premiums based on state regulations, vehicle value, and driver profile
"""

from typing import Dict, Any, List
import math

class AdvancedInsuranceCalculator:
    """Advanced insurance premium calculator"""
    
    def __init__(self):
        # Base annual premium rates by state (simplified)
        self.state_base_rates = {
            'AL': 1420, 'AK': 1180, 'AZ': 1290, 'AR': 1380, 'CA': 1760, 'CO': 1340, 'CT': 1510,
            'DE': 1440, 'FL': 2059, 'GA': 1450, 'HI': 1200, 'ID': 1050, 'IL': 1240, 'IN': 1080,
            'IA': 1050, 'KS': 1150, 'KY': 1350, 'LA': 2298, 'ME': 1020, 'MD': 1380, 'MA': 1175,
            'MI': 1980, 'MN': 1240, 'MS': 1350, 'MO': 1250, 'MT': 1220, 'NE': 1180, 'NV': 1368,
            'NH': 1050, 'NJ': 1590, 'NM': 1300, 'NY': 1470, 'NC': 1100, 'ND': 1240, 'OH': 1050,
            'OK': 1420, 'OR': 1180, 'PA': 1340, 'RI': 1470, 'SC': 1340, 'SD': 1240, 'TN': 1180,
            'TX': 1550, 'UT': 1170, 'VT': 1050, 'VA': 1180, 'WA': 1240, 'WV': 1390, 'WI': 1100, 'WY': 1240
        }
        
        # Age-based multipliers
        self.age_multipliers = {
            16: 3.5, 17: 3.2, 18: 2.8, 19: 2.5, 20: 2.2, 21: 2.0, 22: 1.8, 23: 1.6, 24: 1.4,
            25: 1.2, 26: 1.1, 27: 1.0, 28: 0.95, 29: 0.9, 30: 0.85, 35: 0.8, 40: 0.75, 
            45: 0.7, 50: 0.68, 55: 0.7, 60: 0.75, 65: 0.8, 70: 0.9, 75: 1.1, 80: 1.3
        }
        
        # Coverage type multipliers
        self.coverage_multipliers = {
            'basic': 0.6,        # Liability only
            'standard': 1.0,     # Liability + comprehensive
            'comprehensive': 1.4, # Full coverage
            'premium': 1.8       # Maximum protection
        }
        
        # Vehicle value brackets (affects premium)
        self.vehicle_value_brackets = [
            (0, 15000, 0.85),      # Lower value vehicles
            (15000, 30000, 1.0),   # Average value vehicles
            (30000, 50000, 1.15),  # Higher value vehicles
            (50000, 80000, 1.35),  # Luxury vehicles
            (80000, float('inf'), 1.6)  # Super luxury vehicles
        ]
        
        # Multi-vehicle discounts
        self.multi_vehicle_discounts = {
            1: 1.0,    # No discount
            2: 0.9,    # 10% discount
            3: 0.85,   # 15% discount
            4: 0.8,    # 20% discount
            5: 0.75    # 25% discount (max)
        }
        
        # Annual mileage multipliers
        self.mileage_multipliers = {
            (0, 7500): 0.9,
            (7500, 12000): 1.0,
            (12000, 15000): 1.05,
            (15000, 20000): 1.1,
            (20000, 30000): 1.2,
            (30000, float('inf')): 1.35
        }
    
    def calculate_annual_premium(self, vehicle_value: float, vehicle_make: str,
                               vehicle_year: int, driver_age: int, state: str,
                               coverage_type: str, annual_mileage: int,
                               num_vehicles: int = 1, regional_multiplier: float = 1.0,
                               **kwargs) -> float:
        """Calculate annual insurance premium"""
        
        # Extract additional parameters if provided
        vehicle_model = kwargs.get('vehicle_model', '')  # Accept but don't use for now
        
        # Base premium for the state
        base_premium = self.state_base_rates.get(state, 1300)
        
        # Age adjustment
        age_multiplier = self._get_age_multiplier(driver_age)
        
        # Coverage type adjustment
        coverage_multiplier = self.coverage_multipliers.get(coverage_type, 1.0)
        
        # Vehicle value adjustment
        value_multiplier = self._get_vehicle_value_multiplier(vehicle_value)
        
        # Vehicle age adjustment (newer cars cost more to insure)
        vehicle_age = 2024 - vehicle_year
        age_adjustment = max(0.7, 1.0 - (vehicle_age * 0.03))  # 3% reduction per year, min 70%
        
        # Brand adjustment (some brands cost more to insure)
        brand_multiplier = self._get_brand_multiplier(vehicle_make)
        
        # Mileage adjustment
        mileage_multiplier = self._get_mileage_multiplier(annual_mileage)
        
        # Multi-vehicle discount
        multi_vehicle_discount = self.multi_vehicle_discounts.get(
            min(num_vehicles, 5), self.multi_vehicle_discounts[5]
        )
        
        # Calculate final premium
        annual_premium = (
            base_premium * 
            age_multiplier * 
            coverage_multiplier * 
            value_multiplier * 
            age_adjustment * 
            brand_multiplier * 
            mileage_multiplier * 
            multi_vehicle_discount * 
            regional_multiplier
        )
        
        return annual_premium
    
    def calculate_lease_insurance(self, vehicle_value: float, vehicle_make: str,
                                vehicle_year: int, driver_age: int, state: str,
                                regional_multiplier: float = 1.0, **kwargs) -> float:
        """Calculate insurance for leased vehicles (typically requires comprehensive)"""
        
        # Leased vehicles typically require comprehensive coverage
        return self.calculate_annual_premium(
            vehicle_value=vehicle_value,
            vehicle_make=vehicle_make,
            vehicle_year=vehicle_year,
            driver_age=driver_age,
            state=state,
            coverage_type='comprehensive',  # Required for leases
            annual_mileage=12000,  # Standard assumption
            num_vehicles=1,
            regional_multiplier=regional_multiplier,
            **kwargs  # Pass through any additional parameters
        ) * 1.1  # 10% premium for lease requirements (gap insurance, etc.)
    
    def _get_age_multiplier(self, age: int) -> float:
        """Get age-based multiplier"""
        # Find the closest age in our lookup table
        if age <= 16:
            return self.age_multipliers[16]
        elif age >= 80:
            return self.age_multipliers[80]
        
        # Find exact match or interpolate
        if age in self.age_multipliers:
            return self.age_multipliers[age]
        
        # Linear interpolation between known points
        ages = sorted(self.age_multipliers.keys())
        for i in range(len(ages) - 1):
            if ages[i] <= age <= ages[i + 1]:
                ratio = (age - ages[i]) / (ages[i + 1] - ages[i])
                return (self.age_multipliers[ages[i]] * (1 - ratio) + 
                       self.age_multipliers[ages[i + 1]] * ratio)
        
        return 1.0  # Fallback
    
    def _get_vehicle_value_multiplier(self, vehicle_value: float) -> float:
        """Get vehicle value-based multiplier"""
        for min_val, max_val, multiplier in self.vehicle_value_brackets:
            if min_val <= vehicle_value < max_val:
                return multiplier
        return 1.0
    
    def _get_brand_multiplier(self, make: str) -> float:
        """Get brand-based insurance multiplier"""
        # Some brands are more expensive to insure due to repair costs, theft rates, etc.
        brand_multipliers = {
            'BMW': 1.25,
            'Mercedes-Benz': 1.3,
            'Audi': 1.2,
            'Lexus': 1.15,
            'Acura': 1.1,
            'Infiniti': 1.1,
            'Cadillac': 1.15,
            'Toyota': 0.9,
            'Honda': 0.9,
            'Hyundai': 0.85,
            'Kia': 0.85,
            'Subaru': 0.95,
            'Mazda': 0.95,
            'Chevrolet': 1.0,
            'Ford': 1.05,
            'Ram': 1.1,
            'Jeep': 1.1
        }
        
        return brand_multipliers.get(make, 1.0)
    
    def _get_mileage_multiplier(self, annual_mileage: int) -> float:
        """Get mileage-based multiplier"""
        for (min_miles, max_miles), multiplier in self.mileage_multipliers.items():
            if min_miles <= annual_mileage < max_miles:
                return multiplier
        return 1.35  # High mileage default
    
    def calculate_insurance_comparison(self, vehicles: List[Dict[str, Any]], 
                                     driver_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Compare insurance costs across multiple vehicles"""
        
        comparison_results = []
        
        for vehicle in vehicles:
            annual_premium = self.calculate_annual_premium(
                vehicle_value=vehicle['value'],
                vehicle_make=vehicle['make'],
                vehicle_year=vehicle['year'],
                driver_age=driver_profile['age'],
                state=driver_profile['state'],
                coverage_type=driver_profile.get('coverage_type', 'standard'),
                annual_mileage=driver_profile.get('annual_mileage', 12000),
                num_vehicles=driver_profile.get('num_vehicles', 1),
                regional_multiplier=driver_profile.get('regional_multiplier', 1.0)
            )
            
            comparison_results.append({
                'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
                'annual_premium': annual_premium,
                'monthly_premium': annual_premium / 12,
                'vehicle_value': vehicle['value']
            })
        
        # Sort by premium (lowest first)
        comparison_results.sort(key=lambda x: x['annual_premium'])
        
        return {
            'vehicles': comparison_results,
            'lowest_premium': comparison_results[0] if comparison_results else None,
            'highest_premium': comparison_results[-1] if comparison_results else None,
            'premium_range': (comparison_results[-1]['annual_premium'] - 
                            comparison_results[0]['annual_premium']) if len(comparison_results) > 1 else 0
        }
    
    def get_insurance_insights(self, annual_premium: float, vehicle_value: float,
                             driver_age: int, state: str) -> List[str]:
        """Generate insurance insights and recommendations"""
        
        insights = []
        
        # Premium as percentage of vehicle value
        premium_percentage = (annual_premium / vehicle_value) * 100 if vehicle_value > 0 else 0
        
        if premium_percentage > 15:
            insights.append("Insurance costs are high relative to vehicle value - consider higher deductibles")
        elif premium_percentage < 5:
            insights.append("Insurance costs are reasonable relative to vehicle value")
        
        # Age-based insights
        if driver_age < 25:
            insights.append("Young driver rates are higher - costs will decrease with age and experience")
        elif driver_age > 65:
            insights.append("Senior driver rates may increase - consider defensive driving courses")
        
        # State-specific insights
        high_cost_states = ['FL', 'LA', 'MI', 'CA', 'TX']
        if state in high_cost_states:
            insights.append(f"Insurance costs in {state} are typically above national average")
        
        # General recommendations
        insights.append("Shop around annually - rates can vary significantly between insurers")
        insights.append("Consider bundling with home/renters insurance for discounts")
        insights.append("Maintain good credit and clean driving record to qualify for lower rates")
        
        return insights
    
    def calculate_coverage_options(self, vehicle_value: float, base_premium: float) -> Dict[str, Dict[str, Any]]:
        """Calculate different coverage option costs"""
        
        coverage_options = {}
        
        for coverage_type, multiplier in self.coverage_multipliers.items():
            premium = base_premium * multiplier
            
            coverage_options[coverage_type] = {
                'annual_premium': premium,
                'monthly_premium': premium / 12,
                'coverage_description': self._get_coverage_description(coverage_type)
            }
        
        return coverage_options
    
    def _get_coverage_description(self, coverage_type: str) -> str:
        """Get description of coverage type"""
        descriptions = {
            'basic': 'Liability only - minimum legal requirements',
            'standard': 'Liability + comprehensive + collision',
            'comprehensive': 'Full coverage with higher limits',
            'premium': 'Maximum protection with additional benefits'
        }
        
        return descriptions.get(coverage_type, 'Standard coverage')

# Test function
def test_insurance_calculator():
    """Test the insurance calculator"""
    calculator = AdvancedInsuranceCalculator()
    
    # Test basic premium calculation
    annual_premium = calculator.calculate_annual_premium(
        vehicle_value=35000,
        vehicle_make="Toyota",
        vehicle_year=2023,
        driver_age=30,
        state="CA",
        coverage_type="standard",
        annual_mileage=12000,
        num_vehicles=2
    )
    
    print(f"Annual insurance premium: ${annual_premium:.0f}")
    
    # Test coverage options
    coverage_options = calculator.calculate_coverage_options(35000, annual_premium)
    
    print(f"\nCoverage Options:")
    for coverage_type, details in coverage_options.items():
        print(f"{coverage_type.title()}: ${details['annual_premium']:.0f}/year - {details['coverage_description']}")
    
    # Test insights
    insights = calculator.get_insurance_insights(annual_premium, 35000, 30, "CA")
    print(f"\nInsurance Insights:")
    for insight in insights:
        print(f"• {insight}")

if __name__ == "__main__":
    test_insurance_calculator()