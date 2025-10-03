"""
Maintenance Cost Calculator - Enhanced with Granular Mileage-Based Services
Calculates maintenance costs based on vehicle age, mileage, and detailed service intervals
COMPLETELY REWRITTEN to fix BMW filtering and service selection issues
"""

from typing import Dict, Any, List
import math

class MaintenanceCalculator:
    """Calculator for vehicle maintenance costs with proper brand-specific filtering"""
    
    def __init__(self):
        # Enhanced maintenance costs by service type (in dollars)
        self.service_costs = {
            # OIL CHANGE TYPES (mutually exclusive)
            'oil_change': 65,                # Conventional oil (economy brands)
            'oil_change_synthetic': 85,      # Synthetic oil (mainstream brands)
            'premium_oil_change': 120,       # Premium synthetic (luxury brands)
            
            # BASIC MAINTENANCE
            'tire_rotation': 25,             # Every 6,000-8,000 miles
            'air_filter': 35,               # Every 12,000-20,000 miles
            'cabin_filter': 45,             # Every 12,000-20,000 miles
            'brake_inspection': 50,         # Every 12,000-20,000 miles
            'tire_alignment_check': 80,     # Every 12,000 miles
            'wiper_blade_replacement': 45,  # Every 12,000 miles
            
            # INTERMEDIATE MAINTENANCE
            'brake_fluid_change': 90,       # Every 24,000 miles (2 years)
            'coolant_flush': 150,           # Every 60,000 miles
            'transmission_service': 250,    # Every 60,000-100,000 miles
            'fuel_filter': 85,              # Every 30,000 miles
            'major_service': 400,           # Every 30,000-40,000 miles
            'serpentine_belt_replacement': 130, # Every 60,000-100,000 miles
            
            # MAJOR MAINTENANCE
            'spark_plugs': 180,             # Every 45,000-100,000 miles
            'timing_belt': 800,             # Every 90,000-105,000 miles
            'water_pump': 750,              # Every 90,000-100,000 miles
            
            # WEAR COMPONENTS (only when needed)
            'brake_pads': 280,              # Every 25,000-50,000 miles
            'brake_rotors': 450,            # Every 50,000-80,000 miles
            'tire_replacement_set': 800,    # Every 40,000-60,000 miles
            'battery_replacement': 180,     # Every 4-6 years
            'shock_strut_replacement': 850, # Every 80,000-120,000 miles
            
            # ELECTRIC/HYBRID ONLY
            'ev_battery_inspection': 150,   # EVs only
            'high_voltage_system_check': 200, # EVs/Hybrids only
            'hybrid_battery_check': 120,    # Hybrids only
        }
        
        # Service intervals by mileage
        self.service_intervals = {
            # OIL CHANGES
            'oil_change': 5000,              # Conventional oil
            'oil_change_synthetic': 7500,    # Synthetic oil
            'premium_oil_change': 10000,     # Premium synthetic
            
            # BASIC MAINTENANCE
            'tire_rotation': 7500,           # Every 7,500 miles
            'air_filter': 15000,             # Every 15,000 miles
            'cabin_filter': 15000,           # Every 15,000 miles
            'brake_inspection': 15000,       # Every 15,000 miles
            'tire_alignment_check': 15000,   # Every 15,000 miles
            'wiper_blade_replacement': 15000, # Every 15,000 miles
            
            # INTERMEDIATE MAINTENANCE
            'brake_fluid_change': 30000,     # Every 30,000 miles
            'coolant_flush': 60000,          # Every 60,000 miles
            'transmission_service': 60000,   # Every 60,000 miles
            'fuel_filter': 30000,            # Every 30,000 miles
            'major_service': 30000,          # Every 30,000 miles
            'serpentine_belt_replacement': 80000, # Every 80,000 miles
            
            # MAJOR MAINTENANCE
            'spark_plugs': 60000,            # Every 60,000 miles
            'timing_belt': 90000,            # Every 90,000 miles
            'water_pump': 100000,            # Every 100,000 miles
            
            # WEAR COMPONENTS
            'brake_pads': 40000,             # Average 40,000 miles
            'brake_rotors': 70000,           # Average 70,000 miles
            'tire_replacement_set': 50000,   # Average 50,000 miles
            'battery_replacement': 60000,    # 5 years average (12k miles/year)
            'shock_strut_replacement': 100000, # Every 100,000 miles
            
            # ELECTRIC/HYBRID
            'ev_battery_inspection': 20000,  # Every 20,000 miles
            'high_voltage_system_check': 40000, # Every 40,000 miles
            'hybrid_battery_check': 30000,   # Every 30,000 miles
        }
        
        # Brand-specific service intervals and preferences - COMPREHENSIVE FOR ALL BRANDS
        self.brand_service_configs = {
            # GERMAN LUXURY
            'BMW': {
                'preferred_oil': 'premium_oil_change',
                'oil_interval': 10000,
                'major_service_interval': 40000,
                'brake_inspection_interval': 20000,
                'air_filter_interval': 20000,
                'cabin_filter_interval': 20000,
                'brake_fluid_interval': 24000,
                'coolant_interval': 48000,
                'spark_plug_interval': 80000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',  # Only premium oil
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'  # Not electric (most models)
                ]
            },
            'Mercedes-Benz': {
                'preferred_oil': 'premium_oil_change',
                'oil_interval': 10000,
                'major_service_interval': 40000,
                'brake_inspection_interval': 20000,
                'air_filter_interval': 20000,
                'cabin_filter_interval': 20000,
                'brake_fluid_interval': 24000,
                'coolant_interval': 48000,
                'spark_plug_interval': 80000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Audi': {
                'preferred_oil': 'premium_oil_change',
                'oil_interval': 10000,
                'major_service_interval': 40000,
                'brake_inspection_interval': 20000,
                'air_filter_interval': 20000,
                'cabin_filter_interval': 20000,
                'brake_fluid_interval': 24000,
                'spark_plug_interval': 80000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Porsche': {
                'preferred_oil': 'premium_oil_change',
                'oil_interval': 10000,
                'major_service_interval': 20000,  # Performance cars need more frequent service
                'brake_inspection_interval': 10000,  # Performance braking
                'brake_fluid_interval': 24000,
                'spark_plug_interval': 60000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Volvo': {
                'preferred_oil': 'premium_oil_change',
                'oil_interval': 10000,
                'major_service_interval': 40000,
                'brake_fluid_interval': 24000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            
            # JAPANESE LUXURY
            'Lexus': {
                'preferred_oil': 'premium_oil_change',
                'oil_interval': 10000,
                'major_service_interval': 30000,
                'timing_belt_interval': 105000,
                'transmission_interval': 100000,  # Reliable transmissions
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Acura': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'timing_belt_interval': 105000,
                'transmission_interval': 90000,
                'excluded_services': [
                    'oil_change',  # Use synthetic
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Infiniti': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 60000,  # Similar to Nissan CVT
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            
            # JAPANESE MAINSTREAM
            'Toyota': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 10000,
                'major_service_interval': 30000,
                'timing_belt_interval': 105000,
                'transmission_interval': 100000,
                'excluded_services': [
                    'oil_change',  # Use synthetic
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Honda': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'timing_belt_interval': 105000,
                'transmission_interval': 90000,  # CVT
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Mazda': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 90000,
                'spark_plug_interval': 75000,  # SkyActiv engines
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Subaru': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 6000,  # Boxer engines need more frequent changes
                'major_service_interval': 30000,
                'timing_belt_interval': 105000,
                'transmission_interval': 100000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Nissan': {
                'preferred_oil': 'oil_change',  # Nissan still recommends conventional
                'oil_interval': 5000,
                'major_service_interval': 30000,
                'transmission_interval': 60000,  # CVT needs frequent service
                'brake_inspection_interval': 12000,
                'excluded_services': [
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            
            # AMERICAN BRANDS
            'Ford': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 150000,  # 10-speed auto
                'spark_plug_interval': 100000,  # EcoBoost
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Chevrolet': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 97500,
                'spark_plug_interval': 60000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'GMC': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 97500,
                'spark_plug_interval': 60000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Cadillac': {
                'preferred_oil': 'premium_oil_change',  # Luxury GM brand
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 97500,
                'spark_plug_interval': 80000,  # Premium engines
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Buick': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 97500,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Dodge': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 8000,
                'major_service_interval': 30000,
                'transmission_interval': 60000,  # Some models need frequent service
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Chrysler': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 8000,
                'major_service_interval': 30000,
                'transmission_interval': 60000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Jeep': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 8000,
                'major_service_interval': 30000,
                'transmission_interval': 60000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Ram': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 8000,
                'major_service_interval': 30000,
                'transmission_interval': 60000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            
            # KOREAN BRANDS
            'Hyundai': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'timing_belt_interval': 60000,  # Some engines
                'transmission_interval': 90000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Kia': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'timing_belt_interval': 60000,
                'transmission_interval': 90000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            'Genesis': {
                'preferred_oil': 'premium_oil_change',  # Luxury Korean brand
                'oil_interval': 10000,
                'major_service_interval': 40000,  # Longer luxury intervals
                'brake_inspection_interval': 20000,
                'spark_plug_interval': 80000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
            
            # ELECTRIC VEHICLES
            'Tesla': {
                'preferred_oil': None,  # No oil changes for EVs
                'tire_rotation_interval': 6250,
                'brake_inspection_interval': 25000,  # Regen braking extends brake life
                'cabin_filter_interval': 24000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic', 'premium_oil_change',  # No ICE
                    'spark_plugs', 'timing_belt', 'transmission_service',  # No ICE components
                    'fuel_filter', 'coolant_flush', 'water_pump',  # Different systems
                    'serpentine_belt_replacement',  # No traditional belt system
                    'hybrid_battery_check'  # Pure EV, not hybrid
                ],
                'required_services': ['ev_battery_inspection', 'high_voltage_system_check']
            },
            'Rivian': {
                'preferred_oil': None,
                'tire_rotation_interval': 7500,
                'brake_inspection_interval': 25000,
                'cabin_filter_interval': 24000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic', 'premium_oil_change',
                    'spark_plugs', 'timing_belt', 'transmission_service',
                    'fuel_filter', 'coolant_flush', 'water_pump',
                    'serpentine_belt_replacement', 'hybrid_battery_check'
                ],
                'required_services': ['ev_battery_inspection', 'high_voltage_system_check']
            },
            'Lucid': {
                'preferred_oil': None,
                'tire_rotation_interval': 7500,
                'brake_inspection_interval': 25000,
                'cabin_filter_interval': 24000,
                'excluded_services': [
                    'oil_change', 'oil_change_synthetic', 'premium_oil_change',
                    'spark_plugs', 'timing_belt', 'transmission_service',
                    'fuel_filter', 'coolant_flush', 'water_pump',
                    'serpentine_belt_replacement', 'hybrid_battery_check'
                ],
                'required_services': ['ev_battery_inspection', 'high_voltage_system_check']
            },
            
            # OTHER BRANDS
            'Mitsubishi': {
                'preferred_oil': 'oil_change_synthetic',
                'oil_interval': 7500,
                'major_service_interval': 30000,
                'transmission_interval': 60000,
                'excluded_services': [
                    'oil_change',
                    'ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check'
                ]
            },
        }
        
        # Brand reliability multipliers
        self.brand_multipliers = {
            # Most Reliable (Lower costs)
            'Toyota': 0.85, 'Lexus': 0.88, 'Honda': 0.90, 'Acura': 0.92, 'Mazda': 0.93,
            # Above Average
            'Hyundai': 0.98, 'Kia': 0.98, 'Subaru': 0.95,
            # Average
            'Ford': 1.10, 'Chevrolet': 1.12, 'GMC': 1.12, 'Nissan': 1.15,
            # Luxury (Premium parts)
            'BMW': 1.35, 'Mercedes-Benz': 1.40, 'Audi': 1.32, 'Volvo': 1.28,
            # Electric (Lower maintenance)
            'Tesla': 0.75
        }
        
        # Age-based multipliers
        self.age_multipliers = {
            0: 0.5, 1: 0.6, 2: 0.7, 3: 0.9, 4: 1.0,
            5: 1.2, 6: 1.4, 7: 1.6, 8: 1.9, 9: 2.2, 10: 2.5
        }
        
        # Shop type multipliers
        self.shop_multipliers = {
            'dealership': 1.3, 'independent': 1.0, 'chain': 1.1, 'specialty': 1.2
        }

    def is_electric_vehicle(self, make: str, model: str = '') -> bool:
        """Determine if vehicle is electric"""
        make = make.upper()
        model = model.lower()
        
        if make == 'TESLA':
            return True
        
        electric_models = [
            'leaf', 'bolt', 'volt', 'model 3', 'model s', 'model x', 'model y',
            'ioniq electric', 'kona electric', 'niro ev', 'e-tron', 'i3', 'i4',
            'taycan', 'mustang mach-e', 'lightning', 'lucid air'
        ]
        
        return any(em in model for em in electric_models)

    def is_hybrid_vehicle(self, make: str, model: str = '') -> bool:
        """Determine if vehicle is hybrid"""
        model = model.lower()
        
        hybrid_keywords = ['hybrid', 'prius', 'camry hybrid', 'accord hybrid', 'rav4 hybrid']
        return any(hk in model for hk in hybrid_keywords)

    def get_brand_config(self, make: str) -> Dict[str, Any]:
        """Get brand-specific configuration"""
        return self.brand_service_configs.get(make, {
            'preferred_oil': 'oil_change_synthetic',
            'oil_interval': 7500,
            'excluded_services': ['ev_battery_inspection', 'high_voltage_system_check', 'hybrid_battery_check']
        })

    def get_applicable_services(self, make: str, model: str = '') -> List[str]:
        """Get list of services applicable to this vehicle"""
        brand_config = self.get_brand_config(make)
        excluded = brand_config.get('excluded_services', [])
        
        # Start with all services
        applicable = list(self.service_intervals.keys())
        
        # Remove excluded services
        applicable = [s for s in applicable if s not in excluded]
        
        # Handle oil change preferences
        preferred_oil = brand_config.get('preferred_oil')
        if preferred_oil:
            # Remove other oil change types
            oil_types = ['oil_change', 'oil_change_synthetic', 'premium_oil_change']
            applicable = [s for s in applicable if s not in oil_types or s == preferred_oil]
        
        # Add required services for EVs
        if self.is_electric_vehicle(make, model):
            required = brand_config.get('required_services', [])
            for req in required:
                if req not in applicable:
                    applicable.append(req)
        
        return applicable

    def get_service_interval(self, service_type: str, make: str) -> int:
        """Get brand-specific service interval"""
        brand_config = self.get_brand_config(make)
        
        # Check for brand-specific interval
        interval_key = f"{service_type.replace('_change', '').replace('_replacement', '').replace('_service', '')}_interval"
        brand_interval = brand_config.get(interval_key)
        
        if brand_interval:
            return brand_interval
        
        # Return default interval
        return self.service_intervals.get(service_type, 15000)

    def is_wear_component_needed(self, service_type: str, total_mileage: int, vehicle_age: int) -> bool:
        """Determine if wear component replacement is actually needed"""
        wear_thresholds = {
            'brake_pads': 30000,           # Minimum mileage before brake pads typically need replacement
            'brake_rotors': 60000,         # Minimum mileage for rotor replacement
            'tire_replacement_set': 40000, # Minimum tire life
            'battery_replacement': 48000,  # 4 years minimum (4 * 12k miles)
            'shock_strut_replacement': 80000, # 80k miles minimum
        }
        
        if service_type in wear_thresholds:
            min_mileage = wear_thresholds[service_type]
            
            # For battery, also consider age
            if service_type == 'battery_replacement':
                return total_mileage >= min_mileage or vehicle_age >= 4
            
            return total_mileage >= min_mileage
        
        return True  # Non-wear components are always applicable

    def calculate_annual_maintenance(self, vehicle_make: str, vehicle_year: int, 
                                   current_year: int, annual_mileage: int, 
                                   driving_style: str = 'normal', 
                                   shop_type: str = 'independent',
                                   regional_multiplier: float = 1.0) -> float:
        """Calculate annual maintenance costs"""
        
        vehicle_age = current_year - vehicle_year
        
        # Get applicable services for this brand
        applicable_services = self.get_applicable_services(vehicle_make)
        
        annual_cost = 0
        
        for service_type in applicable_services:
            # Get service interval
            interval = self.get_service_interval(service_type, vehicle_make)
            
            # Calculate frequency
            services_per_year = annual_mileage / interval
            
            # Get cost
            base_cost = self.service_costs.get(service_type, 50)
            
            # Apply multipliers
            brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
            shop_multiplier = self.shop_multipliers.get(shop_type, 1.0)
            
            adjusted_cost = base_cost * brand_multiplier * shop_multiplier * regional_multiplier
            annual_cost += adjusted_cost * services_per_year
        
        # Add wear-based costs for older vehicles
        if vehicle_age > 3:
            wear_cost = self._calculate_wear_maintenance(
                vehicle_age, annual_mileage, driving_style, vehicle_make, shop_type, regional_multiplier
            )
            annual_cost += wear_cost
        
        return annual_cost

    def _calculate_wear_maintenance(self, vehicle_age: int, annual_mileage: int,
                                  driving_style: str, vehicle_make: str,
                                  shop_type: str, regional_multiplier: float) -> float:
        """Calculate wear-based maintenance costs"""
        
        base_wear_cost = 150  # Reduced base cost
        age_multiplier = self.age_multipliers.get(min(vehicle_age, 10), 2.5)
        
        driving_multipliers = {'gentle': 0.8, 'normal': 1.0, 'aggressive': 1.3}
        driving_multiplier = driving_multipliers.get(driving_style, 1.0)
        
        mileage_multiplier = 1.0 + (max(0, annual_mileage - 12000) / 12000) * 0.2
        
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        shop_multiplier = self.shop_multipliers.get(shop_type, 1.0)
        
        return (base_wear_cost * age_multiplier * driving_multiplier * 
                mileage_multiplier * brand_multiplier * shop_multiplier * regional_multiplier)

    def get_maintenance_schedule(self, annual_mileage: int, years: int, 
                               starting_mileage: int = 0, vehicle_make: str = 'Toyota',
                               driving_style: str = 'normal', vehicle_model: str = '') -> List[Dict[str, Any]]:
        """Generate maintenance schedule with proper filtering"""
        
        schedule = []
        total_mileage = starting_mileage
        
        # Get applicable services for this vehicle
        applicable_services = self.get_applicable_services(vehicle_make, vehicle_model)
        
        for year in range(1, years + 1):
            total_mileage += annual_mileage
            year_services = []
            vehicle_age = year
            
            for service_type in applicable_services:
                # Get service interval
                interval = self.get_service_interval(service_type, vehicle_make)
                
                # Calculate services due this year
                previous_total_mileage = starting_mileage + (annual_mileage * (year - 1))
                services_due_by_end_of_year = int(total_mileage / interval)
                services_due_by_end_of_previous_year = int(previous_total_mileage / interval)
                services_this_year = services_due_by_end_of_year - services_due_by_end_of_previous_year
                
                # Check if wear component is actually needed
                if services_this_year > 0:
                    if not self.is_wear_component_needed(service_type, total_mileage, vehicle_age):
                        continue
                    
                    base_cost = self.service_costs.get(service_type, 50)
                    
                    year_services.append({
                        'service': service_type.replace('_', ' ').title(),
                        'frequency': services_this_year,
                        'cost_per_service': base_cost,
                        'total_cost': base_cost * services_this_year,
                        'due_at_mileage': int((services_due_by_end_of_previous_year + 1) * interval),
                        'interval': interval,
                        'interval_based': True
                    })
            
            # Sort by due mileage
            year_services.sort(key=lambda x: x['due_at_mileage'])
            
            schedule.append({
                'year': year,
                'total_mileage': total_mileage,
                'starting_year_mileage': previous_total_mileage,
                'ending_year_mileage': total_mileage,
                'services': year_services,
                'total_year_cost': sum(service['total_cost'] for service in year_services)
            })
        
        return schedule

    def calculate_lease_maintenance(self, lease_year: int, annual_mileage: int,
                                  vehicle_make: str, shop_type: str,
                                  regional_multiplier: float = 1.0) -> float:
        """Calculate lease maintenance with warranty coverage"""
        
        base_cost = self.calculate_annual_maintenance(
            vehicle_make, 2024, 2024 + lease_year, annual_mileage, 
            'normal', 'dealership', regional_multiplier
        )
        
        # Apply warranty discount
        if lease_year <= 2:
            warranty_discount = 0.6
        elif lease_year <= 3:
            warranty_discount = 0.4
        else:
            warranty_discount = 0.2
        
        return base_cost * (1 - warranty_discount)

    def get_maintenance_insights(self, vehicle_make: str, vehicle_age: int, 
                               annual_mileage: int) -> List[str]:
        """Generate maintenance insights"""
        
        insights = []
        
        # Brand-specific insights
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        if brand_multiplier < 0.95:
            insights.append(f"✅ {vehicle_make} vehicles have excellent reliability and lower maintenance costs")
        elif brand_multiplier > 1.3:
            insights.append(f"💰 {vehicle_make} vehicles use premium parts, resulting in higher service costs")
        
        # Age-specific insights
        if vehicle_age <= 2:
            insights.append("🛡️ Most repairs covered under warranty")
        elif vehicle_age <= 5:
            insights.append("⚡ Key maintenance years - follow service schedule closely")
        else:
            insights.append("🔧 Older vehicle - expect more frequent repairs")
        
        # Mileage insights
        if annual_mileage > 15000:
            insights.append("🚗 High mileage driving - consider shorter service intervals")
        elif annual_mileage < 8000:
            insights.append("🕒 Low mileage - follow time-based service intervals")
        
        # Brand-specific service advice
        if vehicle_make in ['BMW', 'Mercedes-Benz', 'Audi']:
            insights.append("🏁 Follow manufacturer's condition-based service system")
        elif vehicle_make == 'Tesla':
            insights.append("⚡ Minimal maintenance required - focus on tires and brakes")
        elif vehicle_make in ['Toyota', 'Honda']:
            insights.append("🔧 Extended service intervals possible with synthetic oil")
        
        return insights

# Test function
def test_maintenance_calculator():
    """Test the maintenance calculator"""
    calculator = MaintenanceCalculator()
    
    print("=== BMW 530i MAINTENANCE TEST ===\n")
    
    # Test BMW 530i specifically
    schedule = calculator.get_maintenance_schedule(
        annual_mileage=12000,
        years=1,
        starting_mileage=88000,
        vehicle_make="BMW",
        vehicle_model="530i"
    )
    
    print("BMW 530i (88k miles, 12k miles/year):")
    for year_data in schedule:
        print(f"Year {year_data['year']}: ${year_data['total_year_cost']:.0f}")
        for service in year_data['services']:
            print(f"  • {service['service']}: {service['frequency']}x @ ${service['cost_per_service']:.0f} = ${service['total_cost']:.0f}")
    
    # Test applicable services
    print(f"\nBMW Applicable Services:")
    services = calculator.get_applicable_services("BMW", "530i")
    for service in services:
        interval = calculator.get_service_interval(service, "BMW")
        cost = calculator.service_costs.get(service, 0)
        print(f"  • {service.replace('_', ' ').title()}: Every {interval:,} miles (${cost})")

if __name__ == "__main__":
    test_maintenance_calculator()