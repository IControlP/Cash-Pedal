"""
Maintenance Cost Calculator
Calculates maintenance costs based on vehicle age, mileage, and service intervals
"""

from typing import Dict, Any, List
import math

class MaintenanceCalculator:
    """Calculator for vehicle maintenance costs"""
    
    def __init__(self):
        # Base maintenance costs by service type (in dollars)
        self.service_costs = {
            'oil_change': 65,
            'tire_rotation': 25,
            'air_filter': 35,
            'cabin_filter': 45,
            'brake_inspection': 50,
            'brake_pads': 350,
            'brake_rotors': 450,
            'transmission_service': 200,
            'coolant_flush': 150,
            'spark_plugs': 180,
            'timing_belt': 800,
            'major_service': 400,
            'differential_service': 120,
            'fuel_filter': 85,
            'battery_replacement': 180,
            'alternator': 650,
            'starter': 550,
            'water_pump': 750
        }
        
        # Service intervals by mileage
        self.service_intervals = {
            'oil_change': 7500,          # Every 7,500 miles
            'tire_rotation': 7500,       # Every 7,500 miles
            'air_filter': 15000,         # Every 15,000 miles
            'cabin_filter': 15000,       # Every 15,000 miles
            'brake_inspection': 15000,   # Every 15,000 miles
            'transmission_service': 60000, # Every 60,000 miles
            'coolant_flush': 60000,      # Every 60,000 miles
            'spark_plugs': 45000,        # Every 45,000 miles
            'major_service': 30000,      # Every 30,000 miles
            'differential_service': 45000, # Every 45,000 miles
            'fuel_filter': 30000,        # Every 30,000 miles
        }
        
        # Brand reliability multipliers
        self.brand_multipliers = {
            'Toyota': 0.85,      # Lower maintenance costs
            'Honda': 0.87,
            'Mazda': 0.90,
            'Hyundai': 0.92,
            'Kia': 0.92,
            'Nissan': 0.95,
            'Subaru': 0.98,
            'Chevrolet': 1.05,   # Average maintenance costs
            'Ford': 1.08,
            'Ram': 1.12,
            'BMW': 1.35,         # Higher maintenance costs
            'Mercedes-Benz': 1.40,
            'Audi': 1.32,
            'Volkswagen': 1.15,
            'Volvo': 1.25
        }
        
        # Shop type multipliers
        self.shop_multipliers = {
            'independent': 0.85,    # 15% discount
            'dealership': 1.20,     # 20% premium
            'specialist': 1.10      # 10% premium
        }
        
        # Age-based wear factors
        self.age_multipliers = {
            1: 0.7,   # New car, mostly warranty
            2: 0.8,   # Still under warranty
            3: 1.0,   # Baseline
            4: 1.1,   # Starting to need more repairs
            5: 1.2,   # More frequent repairs
            6: 1.4,   # Higher repair probability
            7: 1.6,   # Aging components
            8: 1.8,   # Major components may fail
            9: 2.0,   # Higher maintenance needs
            10: 2.2   # Significant aging
        }
    
    def calculate_annual_maintenance(self, vehicle_make: str, vehicle_year: int,
                                   current_year: int, annual_mileage: int,
                                   driving_style: str, shop_type: str,
                                   regional_multiplier: float = 1.0,
                                   **kwargs) -> float:
        """Calculate annual maintenance costs for a purchased vehicle"""
        
        vehicle_age = current_year
        
        # Calculate routine maintenance
        routine_cost = self._calculate_routine_maintenance(
            annual_mileage, vehicle_age, vehicle_make, shop_type, regional_multiplier
        )
        
        # Calculate wear-based maintenance
        wear_cost = self._calculate_wear_maintenance(
            vehicle_age, annual_mileage, driving_style, vehicle_make, shop_type, regional_multiplier
        )
        
        total_annual_cost = routine_cost + wear_cost
        
        return total_annual_cost
    
    def calculate_annual_maintenance_cost(self, vehicle_make: str, vehicle_year: int = 2020,
                                        current_year: int = 1, annual_mileage: int = 12000,
                                        driving_style: str = 'normal', shop_type: str = 'independent',
                                        regional_multiplier: float = 1.0, **kwargs) -> float:
        """Calculate annual maintenance costs - alias method"""
        return self.calculate_annual_maintenance(
            vehicle_make, vehicle_year, current_year, annual_mileage,
            driving_style, shop_type, regional_multiplier
        )
    
    def calculate_lease_maintenance(self, vehicle_make: str, vehicle_year: int,
                                  lease_year: int, annual_mileage: int,
                                  regional_multiplier: float = 1.0) -> float:
        """Calculate maintenance costs for leased vehicles (typically lower due to warranty)"""
        
        # Leased vehicles typically have lower maintenance costs due to warranty coverage
        base_cost = self.calculate_annual_maintenance(
            vehicle_make=vehicle_make,
            vehicle_year=vehicle_year,
            current_year=lease_year,
            annual_mileage=annual_mileage,
            driving_style='normal',
            shop_type='dealership',  # Leases often require dealership service
            regional_multiplier=regional_multiplier
        )
        
        # Apply lease discount based on warranty coverage
        if lease_year <= 2:
            warranty_discount = 0.6  # 60% discount for full warranty coverage
        elif lease_year <= 3:
            warranty_discount = 0.4  # 40% discount for extended coverage
        else:
            warranty_discount = 0.2  # 20% discount for limited coverage
        
        return base_cost * (1 - warranty_discount)
    
    def _calculate_routine_maintenance(self, annual_mileage: int, vehicle_age: int,
                                     vehicle_make: str, shop_type: str,
                                     regional_multiplier: float) -> float:
        """Calculate routine maintenance costs"""
        
        annual_cost = 0
        
        # Calculate frequency of each service type based on annual mileage
        for service_type, interval in self.service_intervals.items():
            services_per_year = annual_mileage / interval
            base_cost = self.service_costs[service_type]
            
            # Apply multipliers
            brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
            shop_multiplier = self.shop_multipliers.get(shop_type, 1.0)
            
            adjusted_cost = base_cost * brand_multiplier * shop_multiplier * regional_multiplier
            annual_cost += adjusted_cost * services_per_year
        
        return annual_cost
    
    def _calculate_wear_maintenance(self, vehicle_age: int, annual_mileage: int,
                                  driving_style: str, vehicle_make: str,
                                  shop_type: str, regional_multiplier: float) -> float:
        """Calculate wear-based maintenance and repair costs"""
        
        # Base wear cost increases with age
        base_wear_cost = 200  # Base annual wear cost
        
        # Age multiplier
        age_multiplier = self.age_multipliers.get(min(vehicle_age, 10), 2.5)
        
        # Driving style multiplier
        driving_multipliers = {
            'gentle': 0.8,
            'normal': 1.0,
            'aggressive': 1.3
        }
        driving_multiplier = driving_multipliers.get(driving_style, 1.0)
        
        # Mileage impact (higher mileage = more wear)
        mileage_multiplier = 1.0 + (max(0, annual_mileage - 12000) / 12000) * 0.3
        
        # Brand and shop multipliers
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        shop_multiplier = self.shop_multipliers.get(shop_type, 1.0)
        
        # Calculate total wear cost
        wear_cost = (base_wear_cost * age_multiplier * driving_multiplier * 
                    mileage_multiplier * brand_multiplier * shop_multiplier * regional_multiplier)
        
        return wear_cost


    def get_maintenance_schedule(self, annual_mileage: int, years: int, starting_mileage: int = 0) -> List[Dict[str, Any]]:
        """Generate a maintenance schedule for planning purposes with starting mileage support"""
        
        schedule = []
        # FIXED: Start from current mileage for used vehicles
        total_mileage = starting_mileage
        
        for year in range(1, years + 1):
            total_mileage += annual_mileage  # Add annual mileage to running total
            year_services = []
            
            # FIXED: Calculate services based on total accumulated mileage
            for service_type, interval in self.service_intervals.items():
                # Calculate services due this year considering starting mileage
                previous_total_mileage = starting_mileage + (annual_mileage * (year - 1))
                
                # How many times has this service been due up to end of this year?
                services_due_by_end_of_year = int(total_mileage / interval)
                
                # How many times was this service due up to end of previous year?
                services_due_by_end_of_previous_year = int(previous_total_mileage / interval)
                
                # Services needed THIS year
                services_this_year = services_due_by_end_of_year - services_due_by_end_of_previous_year
                
                if services_this_year > 0:
                    year_services.append({
                        'service': service_type.replace('_', ' ').title(),
                        'frequency': services_this_year,
                        'cost_per_service': self.service_costs[service_type],
                        'total_cost': self.service_costs[service_type] * services_this_year,
                        'due_at_mileage': int((services_due_by_end_of_previous_year + 1) * interval)
                    })
            
            schedule.append({
                'year': year,
                'total_mileage': total_mileage,
                'starting_year_mileage': previous_total_mileage,
                'ending_year_mileage': total_mileage,
                'services': year_services,
                'total_year_cost': sum(service['total_cost'] for service in year_services)
            })
        
        return schedule

    def calculate_maintenance_comparison(self, vehicles: List[Dict[str, Any]], 
                                       years: int = 5) -> Dict[str, Any]:
        """Compare maintenance costs across multiple vehicles"""
        
        comparison_results = []
        
        for vehicle in vehicles:
            total_maintenance_cost = 0
            
            for year in range(1, years + 1):
                annual_cost = self.calculate_annual_maintenance(
                    vehicle_make=vehicle['make'],
                    vehicle_year=vehicle['year'],
                    current_year=year,
                    annual_mileage=vehicle.get('annual_mileage', 12000),
                    driving_style=vehicle.get('driving_style', 'normal'),
                    shop_type=vehicle.get('shop_type', 'independent'),
                    regional_multiplier=vehicle.get('regional_multiplier', 1.0)
                )
                total_maintenance_cost += annual_cost
            
            comparison_results.append({
                'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
                'total_maintenance_cost': total_maintenance_cost,
                'average_annual_cost': total_maintenance_cost / years,
                'reliability_rating': self._get_reliability_rating(vehicle['make'])
            })
        
        # Sort by total maintenance cost
        comparison_results.sort(key=lambda x: x['total_maintenance_cost'])
        
        return {
            'vehicles': comparison_results,
            'lowest_cost': comparison_results[0],
            'highest_cost': comparison_results[-1],
            'cost_difference': comparison_results[-1]['total_maintenance_cost'] - comparison_results[0]['total_maintenance_cost'],
            'analysis_years': years
        }
    
    def _get_reliability_rating(self, make: str) -> str:
        """Get reliability rating based on brand multiplier"""
        multiplier = self.brand_multipliers.get(make, 1.0)
        
        if multiplier <= 0.90:
            return "Excellent"
        elif multiplier <= 1.0:
            return "Good"
        elif multiplier <= 1.15:
            return "Average"
        elif multiplier <= 1.30:
            return "Below Average"
        else:
            return "Poor"
    
    def get_maintenance_insights(self, vehicle_make: str, vehicle_age: int,
                               annual_mileage: int) -> List[str]:
        """Generate maintenance insights and recommendations"""
        
        insights = []
        
        # Brand-specific insights
        reliability_rating = self._get_reliability_rating(vehicle_make)
        insights.append(f"{vehicle_make} has {reliability_rating.lower()} reliability ratings")
        
        # Age-specific insights
        if vehicle_age <= 3:
            insights.append("Maintenance costs should be low due to warranty coverage")
        elif vehicle_age <= 6:
            insights.append("Moderate maintenance costs as vehicle exits warranty period")
        else:
            insights.append("Higher maintenance costs expected due to vehicle age")
        
        # Mileage insights
        if annual_mileage > 15000:
            insights.append("Higher annual mileage will increase maintenance frequency")
        elif annual_mileage < 8000:
            insights.append("Lower annual mileage may reduce some maintenance costs")
        
        # General recommendations
        insights.append("Regular maintenance can prevent costly major repairs")
        insights.append("Independent shops typically offer 15-20% savings over dealerships")
        
        return insights

# Test function
def test_maintenance_calculator():
    """Test the maintenance calculator"""
    calculator = MaintenanceCalculator()
    
    # Test annual maintenance calculation
    annual_cost = calculator.calculate_annual_maintenance(
        vehicle_make="Toyota",
        vehicle_year=2020,
        current_year=3,
        annual_mileage=12000,
        driving_style="normal",
        shop_type="independent",
        regional_multiplier=1.0
    )
    
    print(f"Annual maintenance cost for 3-year-old Toyota: ${annual_cost:.0f}")
    
    # Test maintenance schedule
    schedule = calculator.get_maintenance_schedule(annual_mileage=12000, years=5)
    
    print("\nMaintenance Schedule (first 3 years):")
    for year_data in schedule[:3]:
        print(f"Year {year_data['year']} ({year_data['total_mileage']:,} miles): ${year_data['total_year_cost']:.0f}")
        for service in year_data['services'][:3]:  # Show first 3 services
            print(f"  • {service['service']}: {service['frequency']}x @ ${service['cost_per_service']} = ${service['total_cost']}")
    
    # Test insights
    insights = calculator.get_maintenance_insights("Toyota", 3, 12000)
    print(f"\nMaintenance Insights:")
    for insight in insights:
        print(f"• {insight}")

if __name__ == "__main__":
    test_maintenance_calculator()