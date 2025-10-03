# vehicle_database.py - Complete Master Vehicle Database Module
# Comprehensive vehicle database with all available makes and models from project files

def safe_import_manufacturers():
    """Safely import manufacturer modules, handling missing files gracefully"""
    manufacturers = {}
    imported_count = 0
    missing_files = []
    
    # Import available manufacturer modules
    manufacturer_modules = {
        'A': 'vehicle_database_a', # Acura, Audi
        'B': 'vehicle_database_b', # BMW, Buick
        'C': 'vehicle_database_c', # Cadillac, Chevrolet, Chrysler
        'D': 'vehicle_database_d', # Dodge
        'F': 'vehicle_database_f', # Ford, Fiat
        'G': 'vehicle_database_g', # GMC
        'H': 'vehicle_database_h', # Honda, Hyundai 
        'I': 'vehicle_database_i', # Infiniti
        'J': 'vehicle_database_j', # Jaguar, Jeep
        'K': 'vehicle_database_k', # Kia
        'L': 'vehicle_database_l', # Lexus, Lincoln
        'M': 'vehicle_database_m', # Mazda, Mercedes-Benz, Mini, Mitsubishi
        'N': 'vehicle_database_n', # Nissan
        'P': 'vehicle_database_p', # Porsche
        'R': 'vehicle_database_r', # Ram
        'S': 'vehicle_database_s', # Subaru
        'T': 'vehicle_database_t', # Tesla, Toyota
        'V': 'vehicle_database_v', # Volkswagen, Volvo
    }
    
    for letter, module_name in manufacturer_modules.items():
        try:
            import importlib
            module = importlib.import_module(f'data.{module_name}')
            data = getattr(module, f'MANUFACTURERS_{letter}', {})
            manufacturers.update(data)
            imported_count += 1
            print(f"✅ Loaded {module_name}: {list(data.keys())}")
        except ImportError as e:
            missing_files.append(f"{module_name}.py")
            print(f"⚠️ Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ Error loading {module_name}: {e}")
    
    return manufacturers, imported_count, missing_files

# Load the vehicle database
try:
    vehicle_database, loaded_count, missing = safe_import_manufacturers()
    print(f"📊 Database Status: {loaded_count} modules loaded, {len(missing)} missing")
    if missing:
        print(f"📝 Missing files: {missing}")
except Exception as e:
    print(f"❌ Critical error loading database: {e}")
    vehicle_database = {}

# Fallback data for basic functionality
FALLBACK_DATABASE = {
    "Chevrolet": {
        "Silverado": {
            "production_years": (2007, 2025),
            "trims_by_year": {
                2020: {"Work Truck": 29895, "LT": 38995, "LTZ": 47395, "High Country": 52395},
                2021: {"Work Truck": 30395, "LT": 39495, "LTZ": 47895, "High Country": 52895},
                2022: {"Work Truck": 30895, "LT": 39995, "LTZ": 48395, "High Country": 53395},
                2023: {"Work Truck": 31395, "LT": 40495, "LTZ": 49395, "High Country": 54395},
                2024: {"Work Truck": 31895, "LT": 40995, "LTZ": 49895, "High Country": 54895},
                2025: {"Work Truck": 32395, "LT": 41495, "LTZ": 50395, "High Country": 55395}
            }
        },
        "Malibu": {
            "production_years": (1997, 2024),
            "trims_by_year": {
                2020: {"L": 23995, "LS": 25995, "LT": 27995},
                2021: {"L": 24495, "LS": 26495, "LT": 28495},
                2022: {"L": 24995, "LS": 26995, "LT": 28995},
                2023: {"L": 24995, "LS": 26995, "LT": 28995},
                2024: {"L": 25495, "LS": 27495, "LT": 29495}
            }
        }
    },
    "Honda": {
        "Civic": {
            "production_years": (1973, 2025),
            "trims_by_year": {
                2020: {"LX": 21250, "Sport": 22300, "EX": 24300, "Touring": 27900},
                2021: {"LX": 21700, "Sport": 22750, "EX": 24750, "Touring": 28300},
                2022: {"LX": 22350, "Sport": 23400, "EX": 25400, "Touring": 29000},
                2023: {"LX": 23950, "Sport": 25050, "EX": 26950, "Touring": 29050},
                2024: {"LX": 24295, "Sport": 25395, "EX": 27295, "Touring": 29395},
                2025: {"LX": 24695, "Sport": 25795, "EX": 27695, "Touring": 29795}
            }
        },
        "Accord": {
            "production_years": (1976, 2025),
            "trims_by_year": {
                2020: {"LX": 24770, "Sport": 28320, "EX-L": 31990, "Touring": 36100},
                2021: {"LX": 25170, "Sport": 28720, "EX-L": 32390, "Touring": 36500},
                2022: {"LX": 25795, "Sport": 29395, "EX-L": 33095, "Touring": 37295},
                2023: {"LX": 27295, "Sport": 30795, "EX-L": 33795, "Touring": 37395},
                2024: {"LX": 27595, "Sport": 31095, "EX-L": 34095, "Touring": 37695},
                2025: {"LX": 27995, "Sport": 31495, "EX-L": 34495, "Touring": 38095}
            }
        },
        "Pilot": {
            "production_years": (2003, 2025),
            "trims_by_year": {
                2020: {"LX": 32250, "EX": 35170, "EX-L": 38270, "Touring": 42020},
                2021: {"LX": 33470, "EX": 36390, "EX-L": 39590, "Touring": 43520},
                2022: {"LX": 35395, "EX": 38295, "EX-L": 41795, "Touring": 45695},
                2023: {"LX": 38395, "EX": 41395, "EX-L": 45395, "Touring": 49395},
                2024: {"LX": 38795, "EX": 41795, "EX-L": 45795, "Touring": 49795},
                2025: {"LX": 39195, "EX": 42195, "EX-L": 46195, "Touring": 50195}
            }
        }
    },
    "Hyundai": {
        "Elantra": {
            "production_years": (1991, 2025),
            "trims_by_year": {
                2020: {"SE": 19650, "SEL": 20750, "Limited": 23000},
                2021: {"SE": 20050, "SEL": 21150, "Limited": 23400},
                2022: {"SE": 20250, "SEL": 21350, "Limited": 24600},
                2023: {"SE": 20650, "SEL": 22400, "Limited": 25000},
                2024: {"SE": 21050, "SEL": 22800, "Limited": 25400},
                2025: {"SE": 21450, "SEL": 23200, "Limited": 25800}
            }
        },
        "Santa Fe": {
            "production_years": (2001, 2025),
            "trims_by_year": {
                2020: {"SE": 26200, "SEL": 29700, "Limited": 35700},
                2021: {"SE": 27200, "SEL": 30700, "Limited": 36700},
                2022: {"SE": 28200, "SEL": 31700, "Limited": 37700},
                2023: {"SE": 29200, "SEL": 32700, "Limited": 38700, "Calligraphy": 42700},
                2024: {"SE": 29700, "SEL": 33200, "Limited": 39200, "Calligraphy": 43200},
                2025: {"SE": 30200, "SEL": 33700, "Limited": 39700, "Calligraphy": 43700}
            }
        }
    },
    "Ram": {
        "1500": {
            "production_years": (2011, 2025),
            "trims_by_year": {
                2020: {"Tradesman": 32095, "Express": 37595, "Big Horn": 39595, "Laramie": 42595, "Limited": 50595},
                2021: {"Tradesman": 32395, "Express": 37895, "Big Horn": 39895, "Laramie": 42895, "Limited": 50895},
                2022: {"Tradesman": 32595, "Express": 38595, "Big Horn": 40595, "Laramie": 43595, "Limited": 51595},
                2023: {"Tradesman": 32895, "Express": 38895, "Big Horn": 40895, "Laramie": 43895, "Limited": 51895},
                2024: {"Tradesman": 33195, "Express": 39195, "Big Horn": 41195, "Laramie": 44195, "Limited": 52195},
                2025: {"Tradesman": 33495, "Express": 39495, "Big Horn": 41495, "Laramie": 44495, "Limited": 52495}
            }
        }
    }
}

# Use loaded database or fallback
if not vehicle_database:
    print("⚠️ Using fallback database with limited vehicle data")
    vehicle_database = FALLBACK_DATABASE

# Core database access functions
def get_all_manufacturers():
    """Get all available manufacturers"""
    return sorted(list(vehicle_database.keys()))

def get_models_for_manufacturer(make):
    """Get all models for a specific manufacturer"""
    return sorted(list(vehicle_database.get(make, {}).keys()))

def get_available_years_for_model(make, model):
    """Get available years for a specific model"""
    model_data = vehicle_database.get(make, {}).get(model, {})
    production_years = model_data.get('production_years', (2000, 2025))
    start_year, end_year = production_years[0], production_years[1]
    return list(range(start_year, end_year + 1))

def get_trims_for_vehicle(make, model, year):
    """Get available trims and their prices for a specific vehicle and year"""
    model_data = vehicle_database.get(make, {}).get(model, {})
    trims_by_year = model_data.get('trims_by_year', {})
    
    # Return exact year if available
    if year in trims_by_year:
        return trims_by_year[year]
    
    # Find closest available year
    available_years = sorted(trims_by_year.keys())
    if not available_years:
        return {"Base": 25000, "Premium": 35000}  # Fallback
    
    # Find closest year within production range
    production_start, production_end = model_data.get('production_years', (2000, 2025))
    if year < production_start:
        closest_year = min(available_years)
    elif year > production_end:
        closest_year = max(available_years)
    else:
        closest_year = min(available_years, key=lambda x: abs(x - year))
    
    return trims_by_year.get(closest_year, {"Base": 25000, "Premium": 35000})

def get_vehicle_trim_price(make, model, trim, year):
    """Get price for a specific trim"""
    trims = get_trims_for_vehicle(make, model, year)
    return trims.get(trim, 25000)  # Default price if trim not found

def validate_vehicle_selection(make, model, year, trim):
    """Validate that the vehicle selection is available"""
    # Check manufacturer
    if make not in vehicle_database:
        return False, f"Manufacturer '{make}' not available"
    
    # Check model
    if model not in vehicle_database[make]:
        return False, f"Model '{model}' not available for {make}"
    
    # Check year
    available_years = get_available_years_for_model(make, model)
    if year not in available_years:
        return False, f"Year {year} not available for {make} {model}"
    
    # Check trim
    available_trims = get_trims_for_vehicle(make, model, year)
    if trim not in available_trims:
        return False, f"Trim '{trim}' not available for {year} {make} {model}"
    
    return True, "Valid selection"

def get_vehicle_characteristics(make, model, year):
    """Get vehicle characteristics for TCO calculations"""
    # Default characteristics - can be enhanced with more detailed data
    characteristics = {
        'reliability_score': 3.5,
        'market_segment': 'standard',
        'is_electric': False,
        'mpg': 25,
        'mpge': 0
    }
    
    # Brand-specific adjustments
    if make.lower() in ['toyota', 'honda', 'hyundai']:
        characteristics['reliability_score'] = 4.0
        characteristics['mpg'] = 28
    elif make.lower() in ['bmw', 'mercedes-benz', 'audi']:
        characteristics['market_segment'] = 'luxury'
        characteristics['mpg'] = 23
    elif make.lower() in ['chevrolet', 'ram'] and 'truck' in model.lower():
        characteristics['market_segment'] = 'truck'
        characteristics['mpg'] = 20
    
    # Model-specific adjustments
    if 'civic' in model.lower() or 'elantra' in model.lower():
        characteristics['market_segment'] = 'compact'
        characteristics['mpg'] = 32
    elif 'pilot' in model.lower() or 'santa fe' in model.lower():
        characteristics['market_segment'] = 'suv'
        characteristics['mpg'] = 24
    elif 'silverado' in model.lower() or '1500' in model.lower():
        characteristics['market_segment'] = 'truck'
        characteristics['mpg'] = 20
    
    # Electric vehicle detection
    if any(term in model.lower() for term in ['electric', 'ev', 'ioniq']):
        characteristics['is_electric'] = True
        characteristics['mpge'] = 120
        characteristics['mpg'] = 0
    
    return characteristics

def get_database_stats():
    """Get statistics about the vehicle database"""
    # Calculate actual year coverage from the data
    all_years = set()
    for make, models in vehicle_database.items():
        for model, model_data in models.items():
            production_years = model_data.get('production_years', (2000, 2025))
            start_year, end_year = production_years[0], production_years[1]
            all_years.update(range(start_year, end_year + 1))
    
    min_year = min(all_years) if all_years else 2000
    max_year = max(all_years) if all_years else 2025
    
    stats = {
        'total_makes': len(vehicle_database),
        'total_models': sum(len(models) for models in vehicle_database.values()),
        'makes_list': list(vehicle_database.keys()),
        'years_covered': (min_year, max_year),
        'total_years': len(all_years),
        'database_source': 'Project files + fallback data'
    }
    
    # Calculate models per make
    stats['models_per_make'] = {
        make: len(models) for make, models in vehicle_database.items()
    }
    
    return stats

def get_all_models_summary():
    """Get a comprehensive summary of all available vehicles"""
    summary = {}
    
    for make, models in vehicle_database.items():
        summary[make] = {}
        for model, model_data in models.items():
            production_years = model_data.get('production_years', (2020, 2025))
            trims_by_year = model_data.get('trims_by_year', {})
            
            # Get latest year's trims and price range
            if trims_by_year:
                latest_year = max(trims_by_year.keys())
                latest_trims = trims_by_year[latest_year]
                price_range = (min(latest_trims.values()), max(latest_trims.values()))
            else:
                latest_year = production_years[1]
                price_range = (25000, 35000)
            
            summary[make][model] = {
                'production_years': production_years,
                'latest_year': latest_year,
                'price_range': price_range,
                'trim_count': len(trims_by_year.get(latest_year, {}))
            }
    
    return summary

# Database search and filtering functions
def search_vehicles_by_price_range(min_price, max_price, year=2024):
    """Find vehicles within a specific price range"""
    results = []
    
    for make, models in vehicle_database.items():
        for model, model_data in models.items():
            trims = get_trims_for_vehicle(make, model, year)
            for trim, price in trims.items():
                if min_price <= price <= max_price:
                    results.append({
                        'make': make,
                        'model': model,
                        'trim': trim,
                        'year': year,
                        'price': price
                    })
    
    return sorted(results, key=lambda x: x['price'])

def get_vehicles_by_segment(segment, year=2024):
    """Get vehicles by market segment"""
    results = []
    
    for make, models in vehicle_database.items():
        for model in models.keys():
            characteristics = get_vehicle_characteristics(make, model, year)
            if characteristics['market_segment'] == segment:
                trims = get_trims_for_vehicle(make, model, year)
                base_price = min(trims.values()) if trims else 25000
                results.append({
                    'make': make,
                    'model': model,
                    'year': year,
                    'base_price': base_price,
                    'characteristics': characteristics
                })
    
    return sorted(results, key=lambda x: x['base_price'])

# Maintenance and legacy support functions
def get_all_makes():
    """Legacy function - get all manufacturers"""
    return get_all_manufacturers()

def get_models_for_make(make):
    """Legacy function - get models for manufacturer"""
    return get_models_for_manufacturer(make)

def get_trims_for_model_and_year(make, model, year):
    """Legacy function - get trims for vehicle and year"""
    return get_trims_for_vehicle(make, model, year)

# Example usage and testing
if __name__ == "__main__":
    print("=== Comprehensive Vehicle Database ===")
    
    # Display database statistics
    stats = get_database_stats()
    print(f"📊 Database Statistics:")
    print(f"   • Total Manufacturers: {stats['total_makes']}")
    print(f"   • Total Models: {stats['total_models']}")
    print(f"   • Years Covered: {stats['years_covered'][0]}-{stats['years_covered'][1]} ({stats['total_years']} years)")
    print(f"   • Available Makes: {', '.join(stats['makes_list'])}")
    
    print(f"\n📋 Models per Manufacturer:")
    for make, count in stats['models_per_make'].items():
        models = get_models_for_manufacturer(make)
        print(f"   • {make}: {count} models ({', '.join(models[:3])}{'...' if len(models) > 3 else ''})")
    
    # Test vehicle lookup
    print(f"\n🔍 Sample Vehicle Data:")
    if stats['total_makes'] > 0:
        test_make = stats['makes_list'][0]
        test_models = get_models_for_manufacturer(test_make)
        if test_models:
            test_model = test_models[0]
            test_year = 2024
            test_trims = get_trims_for_vehicle(test_make, test_model, test_year)
            print(f"   • {test_year} {test_make} {test_model}")
            print(f"   • Available trims: {list(test_trims.keys())}")
            print(f"   • Price range: ${min(test_trims.values()):,} - ${max(test_trims.values()):,}")
            
            # Test characteristics
            characteristics = get_vehicle_characteristics(test_make, test_model, test_year)
            print(f"   • Market segment: {characteristics['market_segment']}")
            print(f"   • Reliability score: {characteristics['reliability_score']}/5")
            print(f"   • Fuel economy: {characteristics['mpg']} MPG")
    
    # Show price range examples
    print(f"\n💰 Sample Price Ranges:")
    budget_vehicles = search_vehicles_by_price_range(20000, 30000, 2024)
    luxury_vehicles = search_vehicles_by_price_range(50000, 70000, 2024)
    
    if budget_vehicles:
        print(f"   • Budget vehicles ($20k-$30k): {len(budget_vehicles)} options")
        for v in budget_vehicles[:3]:
            print(f"     - {v['year']} {v['make']} {v['model']} {v['trim']}: ${v['price']:,}")
    
    if luxury_vehicles:
        print(f"   • Luxury vehicles ($50k-$70k): {len(luxury_vehicles)} options")
        for v in luxury_vehicles[:3]:
            print(f"     - {v['year']} {v['make']} {v['model']} {v['trim']}: ${v['price']:,}")
    
    print(f"\n✅ Database ready for use!")