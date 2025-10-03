"""
Enhanced Depreciation Model - Realistic Version
Calculates vehicle depreciation using market-based curves with comprehensive brand and segment adjustments
"""

from typing import List, Dict, Any
import math

class EnhancedDepreciationModel:
    """Enhanced depreciation model with realistic market-based adjustments"""
    
    def __init__(self):
        # Comprehensive brand depreciation multipliers (relative to average)
        self.brand_multipliers = {
            # Premium Value Retention (0.75-0.85)
            'Toyota': 0.78,      # Excellent retention
            'Honda': 0.80,
            'Lexus': 0.75,       # Best luxury retention
            'Porsche': 0.82,     # Sports car exception
            
            # Good Value Retention (0.85-0.95)  
            'Subaru': 0.88,
            'Mazda': 0.90,
            'Hyundai': 0.92,
            'Kia': 0.94,
            'Acura': 0.85,
            
            # Average Retention (0.95-1.05)
            'Ford': 1.00,
            'Chevrolet': 1.02,
            'GMC': 1.00,
            'Buick': 0.98,
            'Nissan': 1.03,
            'Infiniti': 1.08,
            'Volvo': 1.05,
            
            # Below Average Retention (1.05-1.20)
            'Volkswagen': 1.12,
            'Mini': 1.15,
            'Jaguar': 1.18,
            'Land Rover': 1.20,
            
            # Poor Retention - Luxury (1.15-1.30)
            'BMW': 1.22,         # Reality: BMW depreciates heavily
            'Mercedes-Benz': 1.25, # Reality: Very high depreciation
            'Audi': 1.18,
            'Cadillac': 1.20,
            'Lincoln': 1.25,
            'Genesis': 1.15,
            
            # Poor Retention - Others (1.20-1.35)
            'Chrysler': 1.30,
            'Dodge': 1.28,
            'Jeep': 1.10,        # Exception: Wrangler holds value
            'Ram': 1.05,         # Trucks hold value better
            'Fiat': 1.35,
            'Alfa Romeo': 1.32,
            
            # Special Cases
            'Tesla': 1.15,       # Tech obsolescence risk
            'Rivian': 1.25,      # New EV brand uncertainty
            'Lucid': 1.30,       # Startup premium depreciation
        }
        
        # Realistic segment-specific depreciation curves
        self.segment_curves = {
            # Luxury vehicles depreciate faster early, then plateau
            'luxury': {
                1: 0.25,   2: 0.42,   3: 0.55,   4: 0.65,   5: 0.72,
                6: 0.77,   7: 0.81,   8: 0.84,   9: 0.86,   10: 0.88,
                11: 0.89,  12: 0.90,  13: 0.91,  14: 0.92,  15: 0.93
            },
            
            # Electric vehicles - high early depreciation due to tech changes
            'electric': {
                1: 0.30,   2: 0.50,   3: 0.65,   4: 0.75,   5: 0.82,
                6: 0.86,   7: 0.89,   8: 0.91,   9: 0.92,   10: 0.93,
                11: 0.94,  12: 0.95,  13: 0.95,  14: 0.95,  15: 0.95
            },
            
            # Trucks hold value well, especially popular models
            'truck': {
                1: 0.15,   2: 0.28,   3: 0.38,   4: 0.46,   5: 0.53,
                6: 0.59,   7: 0.64,   8: 0.68,   9: 0.71,   10: 0.74,
                11: 0.76,  12: 0.78,  13: 0.80,  14: 0.82,  15: 0.84
            },
            
            # Sports cars - variable by desirability
            'sports': {
                1: 0.22,   2: 0.38,   3: 0.50,   4: 0.60,   5: 0.68,
                6: 0.74,   7: 0.78,   8: 0.81,   9: 0.83,   10: 0.85,
                11: 0.86,  12: 0.87,  13: 0.88,  14: 0.89,  15: 0.90
            },
            
            # SUVs - popular segment with good retention
            'suv': {
                1: 0.18,   2: 0.32,   3: 0.43,   4: 0.52,   5: 0.60,
                6: 0.66,   7: 0.71,   8: 0.75,   9: 0.78,   10: 0.80,
                11: 0.82,  12: 0.83,  13: 0.84,  14: 0.85,  15: 0.86
            },
            
            # Compact cars - predictable, moderate depreciation
            'compact': {
                1: 0.20,   2: 0.35,   3: 0.47,   4: 0.56,   5: 0.64,
                6: 0.70,   7: 0.75,   8: 0.79,   9: 0.82,   10: 0.84,
                11: 0.86,  12: 0.87,  13: 0.88,  14: 0.89,  15: 0.90
            },
            
            # Sedans - declining segment
            'sedan': {
                1: 0.21,   2: 0.36,   3: 0.48,   4: 0.58,   5: 0.66,
                6: 0.72,   7: 0.77,   8: 0.81,   9: 0.84,   10: 0.86,
                11: 0.88,  12: 0.89,  13: 0.90,  14: 0.91,  15: 0.92
            },
            
            # Economy cars - higher depreciation, less demand
            'economy': {
                1: 0.24,   2: 0.40,   3: 0.52,   4: 0.62,   5: 0.70,
                6: 0.76,   7: 0.81,   8: 0.84,   9: 0.87,   10: 0.89,
                11: 0.90,  12: 0.91,  13: 0.92,  14: 0.93,  15: 0.94
            }
        }
        
        # Standard curve for unclassified vehicles (conservative)
        self.standard_curve = {
            1: 0.20,   2: 0.34,   3: 0.45,   4: 0.54,   5: 0.62,
            6: 0.68,   7: 0.73,   8: 0.77,   9: 0.80,   10: 0.82,
            11: 0.84,  12: 0.85,  13: 0.86,  14: 0.87,  15: 0.88
        }
        
        # High-demand models that buck depreciation trends
        self.high_retention_models = {
            'Toyota': ['Prius', 'Camry', 'Corolla', 'RAV4', 'Highlander', 'Sienna', 'Tundra', 'Tacoma'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Odyssey', 'Ridgeline'],
            'Subaru': ['Outback', 'Forester', 'Impreza', 'WRX', 'Crosstrek'],
            'Lexus': ['RX', 'ES', 'GX', 'LX', 'NX'],
            'Jeep': ['Wrangler'],  # Unique case
            'Ford': ['F-150', 'Bronco'],
            'Chevrolet': ['Corvette', 'Silverado', 'Tahoe'],
            'Porsche': ['911', 'Macan', 'Cayenne'],
            'Tesla': ['Model S', 'Model 3'],  # Leading EVs
        }
        
        # Poor retention models
        self.poor_retention_models = {
            'BMW': ['X6', '7 Series', 'i3', 'i8'],
            'Mercedes-Benz': ['S-Class', 'SL-Class', 'G-Class'],
            'Audi': ['A8', 'R8', 'Q7'],
            'Cadillac': ['Escalade', 'CT6'],
            'Lincoln': ['Navigator', 'Continental'],
            'Chrysler': ['300', 'Pacifica'],
            'Fiat': ['500', '500X'],
            'Jaguar': ['XJ', 'F-Type'],
            'Land Rover': ['Range Rover', 'Discovery']
        }

    def _classify_vehicle_segment(self, make: str, model: str) -> str:
        """Enhanced vehicle segment classification"""
        model_lower = model.lower()
        make_lower = make.lower()
        
        # Electric vehicle detection (more comprehensive)
        ev_terms = ['electric', 'ev', 'volt', 'leaf', 'prius prime', 'ioniq', 
                   'model s', 'model 3', 'model x', 'model y', 'i3', 'i4', 'ix',
                   'etron', 'e-tron', 'taycan', 'lightning', 'bolt', 'clarity']
        if any(term in model_lower for term in ev_terms) or make_lower in ['tesla', 'rivian', 'lucid']:
            return 'electric'
        
        # Luxury brand detection (more comprehensive)
        luxury_brands = ['bmw', 'mercedes-benz', 'audi', 'lexus', 'acura', 'infiniti', 
                        'cadillac', 'lincoln', 'genesis', 'volvo', 'jaguar', 'land rover',
                        'porsche', 'maserati', 'bentley', 'rolls-royce']
        if make_lower in luxury_brands:
            return 'luxury'
        
        # Sports car detection (more comprehensive)
        sports_terms = ['corvette', 'mustang', 'camaro', 'challenger', 'charger',
                       '911', 'cayman', 'boxster', 'gt', 'sport', 'rs', 'm3', 'm5',
                       'amg', 'type r', 'sti', 'wrx', 'z', 'supra', 'nsx']
        if any(term in model_lower for term in sports_terms):
            return 'sports'
        
        # Truck detection (more comprehensive)
        truck_terms = ['f-150', 'f-250', 'f-350', 'silverado', 'sierra', 'ram 1500',
                      'ram 2500', 'tundra', 'tacoma', 'frontier', 'ridgeline', 
                      'colorado', 'canyon', 'ranger', 'gladiator', 'titan']
        if any(term in model_lower for term in truck_terms) or 'truck' in model_lower:
            return 'truck'
        
        # SUV detection (more comprehensive)
        suv_terms = ['suburban', 'tahoe', 'yukon', 'expedition', 'navigator',
                    'escalade', 'pilot', 'passport', 'ridgeline', 'highlander',
                    'rav4', 'cr-v', 'hr-v', 'santa fe', 'tucson', 'sorento',
                    'telluride', 'palisade', 'cx-5', 'cx-9', 'outback', 'forester',
                    'ascent', 'pathfinder', 'armada', 'durango', 'grand cherokee',
                    'cherokee', 'compass', 'renegade', 'wrangler']
        if any(term in model_lower for term in suv_terms) or 'suv' in model_lower:
            return 'suv'
        
        # Compact car detection
        compact_terms = ['civic', 'corolla', 'elantra', 'forte', 'sentra', 'versa',
                        'mazda3', 'impreza', 'crosstrek', 'jetta', 'golf']
        if any(term in model_lower for term in compact_terms):
            return 'compact'
        
        # Economy car detection
        economy_terms = ['spark', 'mirage', 'rio', 'accent', 'yaris', 'fit']
        if any(term in model_lower for term in economy_terms):
            return 'economy'
        
        # Default to sedan for unclassified
        return 'sedan'

    def _get_cumulative_depreciation_rate(self, year: int, segment: str = 'sedan') -> float:
        """Get segment-specific cumulative depreciation rate"""
        
        # Use segment-specific curve if available
        curve = self.segment_curves.get(segment, self.standard_curve)
        
        if year <= 15:
            return curve[year]
        else:
            # Extrapolate for years beyond 15 (vehicles plateau)
            final_rate = curve[15]
            additional_years = year - 15
            # Very slow additional depreciation after 15 years
            return min(0.96, final_rate + (additional_years * 0.005))

    def _calculate_mileage_impact(self, annual_mileage: int) -> float:
        """Enhanced mileage impact calculation with realistic curves"""
        
        # Handle zero/very low mileage specially
        if annual_mileage <= 100:
            return 0.60  # Significant bonus for zero miles
        elif annual_mileage <= 1000:
            # Linear scale from 0.60 to 0.75
            ratio = (annual_mileage - 100) / 900
            return 0.60 + (ratio * 0.15)
        elif annual_mileage <= 5000:
            # Linear scale from 0.75 to 0.85
            ratio = (annual_mileage - 1000) / 4000
            return 0.75 + (ratio * 0.10)
        
        # Standard mileage calculations
        standard_mileage = 12000
        
        if annual_mileage <= standard_mileage:
            # Lower mileage reduces depreciation (more gradual)
            ratio = annual_mileage / standard_mileage
            return 0.85 + (ratio * 0.15)  # Range: 0.85 to 1.0
        else:
            # Higher mileage increases depreciation (more severe penalty)
            if annual_mileage <= 20000:
                # Moderate high mileage
                excess_ratio = (annual_mileage - standard_mileage) / 8000
                return 1.0 + (excess_ratio * 0.25)  # 1.0 to 1.25
            else:
                # Very high mileage - severe penalty
                return min(1.5, 1.25 + ((annual_mileage - 20000) / 20000 * 0.25))

    def _apply_model_specific_adjustments(self, make: str, model: str, base_multiplier: float) -> float:
        """Apply model-specific value retention adjustments"""
        
        # Check for high-retention models
        if make in self.high_retention_models:
            if any(model_name.lower() in model.lower() for model_name in self.high_retention_models[make]):
                return base_multiplier * 0.85  # 15% better retention
        
        # Check for poor-retention models
        if make in self.poor_retention_models:
            if any(model_name.lower() in model.lower() for model_name in self.poor_retention_models[make]):
                return base_multiplier * 1.15  # 15% worse retention
        
        return base_multiplier

    def calculate_depreciation_schedule(self, initial_value: float, vehicle_make: str, 
                                      vehicle_model: str, model_year: int, 
                                      annual_mileage: int, years: int) -> List[Dict[str, Any]]:
        """Enhanced depreciation schedule calculation"""
        
        # Determine market segment
        segment = self._classify_vehicle_segment(vehicle_make, vehicle_model)
        
        # Get base brand multiplier
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        
        # Apply model-specific adjustments
        adjusted_brand_multiplier = self._apply_model_specific_adjustments(
            vehicle_make, vehicle_model, brand_multiplier
        )
        
        # Calculate mileage impact
        mileage_multiplier = self._calculate_mileage_impact(annual_mileage)
        
        # Generate depreciation schedule
        schedule = []
        
        for year in range(1, years + 1):
            # Get segment-specific depreciation rate
            base_cumulative_rate = self._get_cumulative_depreciation_rate(year, segment)
            
            # Apply all adjustments
            adjusted_rate = base_cumulative_rate * adjusted_brand_multiplier * mileage_multiplier
            
            # Cap depreciation (different caps by segment)
            max_depreciation = {
                'luxury': 0.95, 'electric': 0.96, 'economy': 0.94,
                'sedan': 0.92, 'compact': 0.91, 'suv': 0.88,
                'truck': 0.85, 'sports': 0.90
            }
            cap = max_depreciation.get(segment, 0.92)
            adjusted_rate = min(adjusted_rate, cap)
            
            # Calculate vehicle value
            new_value = initial_value * (1 - adjusted_rate)
            
            # Calculate annual depreciation (from previous year)
            if year == 1:
                annual_depreciation = initial_value - new_value
            else:
                previous_value = schedule[-1]['vehicle_value']
                annual_depreciation = previous_value - new_value
            
            schedule.append({
                'year': year,
                'vehicle_value': new_value,
                'annual_depreciation': annual_depreciation,
                'cumulative_depreciation': initial_value - new_value,
                'depreciation_rate': adjusted_rate,
                'segment': segment,
                'brand_multiplier': adjusted_brand_multiplier,
                'mileage_multiplier': mileage_multiplier
            })
        
        return schedule

    def estimate_current_value(self, initial_value: float, vehicle_make: str, 
                             vehicle_model: str, vehicle_age: int, 
                             current_mileage: int) -> float:
        """Estimate current value of existing vehicle"""
        
        if vehicle_age <= 0:
            return initial_value
        
        # Calculate annual mileage
        annual_mileage = current_mileage / max(vehicle_age, 1)
        
        # Get segment and adjustments
        segment = self._classify_vehicle_segment(vehicle_make, vehicle_model)
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        adjusted_brand_multiplier = self._apply_model_specific_adjustments(
            vehicle_make, vehicle_model, brand_multiplier
        )
        mileage_multiplier = self._calculate_mileage_impact(annual_mileage)
        
        # Get depreciation rate
        base_rate = self._get_cumulative_depreciation_rate(vehicle_age, segment)
        final_rate = base_rate * adjusted_brand_multiplier * mileage_multiplier
        
        # Apply cap
        max_depreciation = {
            'luxury': 0.95, 'electric': 0.96, 'economy': 0.94,
            'sedan': 0.92, 'compact': 0.91, 'suv': 0.88,
            'truck': 0.85, 'sports': 0.90
        }
        cap = max_depreciation.get(segment, 0.92)
        final_rate = min(final_rate, cap)
        
        return initial_value * (1 - final_rate)

    def get_depreciation_insights(self, vehicle_make: str, vehicle_model: str, 
                                 initial_value: float, years: int = 5) -> Dict[str, Any]:
        """Enhanced depreciation insights"""
        
        segment = self._classify_vehicle_segment(vehicle_make, vehicle_model)
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        adjusted_multiplier = self._apply_model_specific_adjustments(
            vehicle_make, vehicle_model, brand_multiplier
        )
        
        # Calculate scenarios
        scenarios = {}
        for desc, mileage in [('Low', 8000), ('Average', 12000), ('High', 18000)]:
            schedule = self.calculate_depreciation_schedule(
                initial_value, vehicle_make, vehicle_model, 2024, mileage, years
            )
            scenarios[desc.lower()] = schedule[-1]['vehicle_value'] if schedule else 0
        
        return {
            'market_segment': segment,
            'brand_adjustment': adjusted_multiplier,
            'scenarios': scenarios,
            'retention_rating': self._get_retention_rating(adjusted_multiplier),
            'key_insights': self._generate_enhanced_insights(vehicle_make, vehicle_model, segment, adjusted_multiplier)
        }

    def _get_retention_rating(self, brand_multiplier: float) -> str:
        """Enhanced retention rating"""
        if brand_multiplier <= 0.80:
            return "Exceptional"
        elif brand_multiplier <= 0.90:
            return "Excellent" 
        elif brand_multiplier <= 1.00:
            return "Good"
        elif brand_multiplier <= 1.10:
            return "Average"
        elif brand_multiplier <= 1.20:
            return "Below Average"
        else:
            return "Poor"

    def _generate_enhanced_insights(self, make: str, model: str, segment: str, 
                                  brand_multiplier: float) -> List[str]:
        """Generate enhanced insights about depreciation"""
        insights = []
        
        # Brand insights
        if brand_multiplier <= 0.85:
            insights.append(f"{make} vehicles are known for exceptional value retention")
        elif brand_multiplier >= 1.20:
            insights.append(f"{make} vehicles typically experience faster depreciation, especially luxury models")
        
        # Segment insights  
        segment_advice = {
            'luxury': "Luxury vehicles depreciate rapidly in first 3-5 years, then stabilize",
            'electric': "Electric vehicles face technology obsolescence risk affecting resale value",
            'truck': "Trucks typically hold value very well, especially popular models like F-150",
            'suv': "SUVs generally maintain strong resale value due to continued popularity",
            'compact': "Compact cars offer predictable, moderate depreciation rates",
            'sports': "Sports cars vary widely - iconic models may appreciate, others depreciate quickly"
        }
        if segment in segment_advice:
            insights.append(segment_advice[segment])
        
        # Model-specific insights
        if make in self.high_retention_models:
            if any(model_name.lower() in model.lower() for model_name in self.high_retention_models[make]):
                insights.append(f"The {model} is a high-demand model with above-average value retention")
        
        # General insights
        insights.append("Mileage significantly impacts resale value - consider driving patterns carefully")
        insights.append("Well-maintained vehicles with service records depreciate more slowly")
        
        return insights