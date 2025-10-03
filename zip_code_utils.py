"""
ZIP Code Lookup Utilities
Handles ZIP code validation and auto-population of location data
"""

import re
from typing import Dict, Optional, List, Any

# Comprehensive ZIP code to state mapping (major metro areas and regions)
# In production, this would be a comprehensive database or API call
ZIP_CODE_DATABASE = {
    # Alabama
    '35201': {'state': 'AL', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.11},
    '35203': {'state': 'AL', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.11},
    '36101': {'state': 'AL', 'geography_type': 'Suburban', 'fuel_price': 3.10, 'electricity_rate': 0.10},
    
    # Alaska
    '99501': {'state': 'AK', 'geography_type': 'Urban', 'fuel_price': 4.15, 'electricity_rate': 0.22},
    '99508': {'state': 'AK', 'geography_type': 'Suburban', 'fuel_price': 4.20, 'electricity_rate': 0.23},
    
    # Arizona
    '85001': {'state': 'AZ', 'geography_type': 'Urban', 'fuel_price': 3.85, 'electricity_rate': 0.12},
    '85003': {'state': 'AZ', 'geography_type': 'Urban', 'fuel_price': 3.85, 'electricity_rate': 0.12},
    '85201': {'state': 'AZ', 'geography_type': 'Suburban', 'fuel_price': 3.80, 'electricity_rate': 0.11},
    '85301': {'state': 'AZ', 'geography_type': 'Suburban', 'fuel_price': 3.75, 'electricity_rate': 0.11},
    
    # Arkansas
    '72201': {'state': 'AR', 'geography_type': 'Urban', 'fuel_price': 3.10, 'electricity_rate': 0.09},
    '72701': {'state': 'AR', 'geography_type': 'Suburban', 'fuel_price': 3.05, 'electricity_rate': 0.08},
    
    # California - Major Cities
    '90210': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.75, 'electricity_rate': 0.18},
    '90211': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.75, 'electricity_rate': 0.18},
    '90212': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.75, 'electricity_rate': 0.18},
    '94102': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.85, 'electricity_rate': 0.19},
    '94103': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.85, 'electricity_rate': 0.19},
    '94104': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.85, 'electricity_rate': 0.19},
    '95014': {'state': 'CA', 'geography_type': 'Suburban', 'fuel_price': 4.65, 'electricity_rate': 0.17},
    '92008': {'state': 'CA', 'geography_type': 'Suburban', 'fuel_price': 4.55, 'electricity_rate': 0.16},
    '91401': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.70, 'electricity_rate': 0.17},
    '90501': {'state': 'CA', 'geography_type': 'Suburban', 'fuel_price': 4.60, 'electricity_rate': 0.16},
    '90804': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.65, 'electricity_rate': 0.17},
    '92101': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.55, 'electricity_rate': 0.16},
    '94301': {'state': 'CA', 'geography_type': 'Suburban', 'fuel_price': 4.80, 'electricity_rate': 0.18},
    '95101': {'state': 'CA', 'geography_type': 'Urban', 'fuel_price': 4.70, 'electricity_rate': 0.17},
    
    # Colorado
    '80201': {'state': 'CO', 'geography_type': 'Urban', 'fuel_price': 3.55, 'electricity_rate': 0.11},
    '80202': {'state': 'CO', 'geography_type': 'Urban', 'fuel_price': 3.55, 'electricity_rate': 0.11},
    '80301': {'state': 'CO', 'geography_type': 'Suburban', 'fuel_price': 3.45, 'electricity_rate': 0.10},
    '80401': {'state': 'CO', 'geography_type': 'Suburban', 'fuel_price': 3.40, 'electricity_rate': 0.10},
    
    # Connecticut
    '06101': {'state': 'CT', 'geography_type': 'Urban', 'fuel_price': 3.75, 'electricity_rate': 0.18},
    '06801': {'state': 'CT', 'geography_type': 'Suburban', 'fuel_price': 3.70, 'electricity_rate': 0.17},
    
    # Delaware
    '19801': {'state': 'DE', 'geography_type': 'Suburban', 'fuel_price': 3.45, 'electricity_rate': 0.12},
    '19901': {'state': 'DE', 'geography_type': 'Suburban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    
    # Florida - Major Cities
    '33101': {'state': 'FL', 'geography_type': 'Urban', 'fuel_price': 3.45, 'electricity_rate': 0.12},
    '33102': {'state': 'FL', 'geography_type': 'Urban', 'fuel_price': 3.45, 'electricity_rate': 0.12},
    '33109': {'state': 'FL', 'geography_type': 'Urban', 'fuel_price': 3.50, 'electricity_rate': 0.12},
    '32801': {'state': 'FL', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.11},
    '32802': {'state': 'FL', 'geography_type': 'Suburban', 'fuel_price': 3.30, 'electricity_rate': 0.11},
    '33401': {'state': 'FL', 'geography_type': 'Suburban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    '33601': {'state': 'FL', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.11},
    '32301': {'state': 'FL', 'geography_type': 'Suburban', 'fuel_price': 3.25, 'electricity_rate': 0.10},
    '34601': {'state': 'FL', 'geography_type': 'Suburban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    
    # Georgia
    '30301': {'state': 'GA', 'geography_type': 'Urban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    '30302': {'state': 'GA', 'geography_type': 'Urban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    '30309': {'state': 'GA', 'geography_type': 'Suburban', 'fuel_price': 3.25, 'electricity_rate': 0.09},
    '31401': {'state': 'GA', 'geography_type': 'Suburban', 'fuel_price': 3.20, 'electricity_rate': 0.09},
    
    # Hawaii
    '96801': {'state': 'HI', 'geography_type': 'Urban', 'fuel_price': 4.95, 'electricity_rate': 0.28},
    '96813': {'state': 'HI', 'geography_type': 'Urban', 'fuel_price': 4.90, 'electricity_rate': 0.27},
    
    # Idaho
    '83701': {'state': 'ID', 'geography_type': 'Urban', 'fuel_price': 3.65, 'electricity_rate': 0.08},
    '83201': {'state': 'ID', 'geography_type': 'Suburban', 'fuel_price': 3.60, 'electricity_rate': 0.08},
    
    # Illinois - Chicago Area
    '60601': {'state': 'IL', 'geography_type': 'Urban', 'fuel_price': 3.65, 'electricity_rate': 0.13},
    '60602': {'state': 'IL', 'geography_type': 'Urban', 'fuel_price': 3.65, 'electricity_rate': 0.13},
    '60603': {'state': 'IL', 'geography_type': 'Urban', 'fuel_price': 3.65, 'electricity_rate': 0.13},
    '60007': {'state': 'IL', 'geography_type': 'Suburban', 'fuel_price': 3.55, 'electricity_rate': 0.12},
    '60181': {'state': 'IL', 'geography_type': 'Suburban', 'fuel_price': 3.50, 'electricity_rate': 0.12},
    '62701': {'state': 'IL', 'geography_type': 'Suburban', 'fuel_price': 3.45, 'electricity_rate': 0.11},
    
    # Indiana
    '46201': {'state': 'IN', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.11},
    '46802': {'state': 'IN', 'geography_type': 'Suburban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    
    # Iowa
    '50301': {'state': 'IA', 'geography_type': 'Urban', 'fuel_price': 3.25, 'electricity_rate': 0.10},
    '52401': {'state': 'IA', 'geography_type': 'Suburban', 'fuel_price': 3.20, 'electricity_rate': 0.09},
    
    # Kansas
    '66101': {'state': 'KS', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.11},
    '67201': {'state': 'KS', 'geography_type': 'Suburban', 'fuel_price': 3.10, 'electricity_rate': 0.10},
    
    # Kentucky
    '40201': {'state': 'KY', 'geography_type': 'Urban', 'fuel_price': 3.30, 'electricity_rate': 0.09},
    '40502': {'state': 'KY', 'geography_type': 'Suburban', 'fuel_price': 3.25, 'electricity_rate': 0.09},
    
    # Louisiana
    '70112': {'state': 'LA', 'geography_type': 'Urban', 'fuel_price': 3.05, 'electricity_rate': 0.08},
    '70801': {'state': 'LA', 'geography_type': 'Suburban', 'fuel_price': 3.00, 'electricity_rate': 0.08},
    
    # Maine
    '04101': {'state': 'ME', 'geography_type': 'Urban', 'fuel_price': 3.70, 'electricity_rate': 0.14},
    '04401': {'state': 'ME', 'geography_type': 'Suburban', 'fuel_price': 3.65, 'electricity_rate': 0.13},
    
    # Maryland
    '21201': {'state': 'MD', 'geography_type': 'Urban', 'fuel_price': 3.55, 'electricity_rate': 0.13},
    '20601': {'state': 'MD', 'geography_type': 'Suburban', 'fuel_price': 3.50, 'electricity_rate': 0.12},
    
    # Massachusetts - Boston Area
    '02101': {'state': 'MA', 'geography_type': 'Urban', 'fuel_price': 3.80, 'electricity_rate': 0.19},
    '02102': {'state': 'MA', 'geography_type': 'Urban', 'fuel_price': 3.80, 'electricity_rate': 0.19},
    '02108': {'state': 'MA', 'geography_type': 'Urban', 'fuel_price': 3.85, 'electricity_rate': 0.19},
    '02138': {'state': 'MA', 'geography_type': 'Urban', 'fuel_price': 3.85, 'electricity_rate': 0.19},
    '01701': {'state': 'MA', 'geography_type': 'Suburban', 'fuel_price': 3.75, 'electricity_rate': 0.18},
    
    # Michigan
    '48201': {'state': 'MI', 'geography_type': 'Urban', 'fuel_price': 3.55, 'electricity_rate': 0.12},
    '48202': {'state': 'MI', 'geography_type': 'Urban', 'fuel_price': 3.55, 'electricity_rate': 0.12},
    '48104': {'state': 'MI', 'geography_type': 'Suburban', 'fuel_price': 3.45, 'electricity_rate': 0.11},
    '49503': {'state': 'MI', 'geography_type': 'Suburban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    
    # Minnesota
    '55401': {'state': 'MN', 'geography_type': 'Urban', 'fuel_price': 3.45, 'electricity_rate': 0.11},
    '55101': {'state': 'MN', 'geography_type': 'Urban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    
    # Mississippi
    '39201': {'state': 'MS', 'geography_type': 'Urban', 'fuel_price': 3.10, 'electricity_rate': 0.10},
    '38601': {'state': 'MS', 'geography_type': 'Suburban', 'fuel_price': 3.05, 'electricity_rate': 0.09},
    
    # Missouri
    '63101': {'state': 'MO', 'geography_type': 'Urban', 'fuel_price': 3.20, 'electricity_rate': 0.10},
    '64101': {'state': 'MO', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.10},
    
    # Montana
    '59101': {'state': 'MT', 'geography_type': 'Suburban', 'fuel_price': 3.60, 'electricity_rate': 0.10},
    '59701': {'state': 'MT', 'geography_type': 'Suburban', 'fuel_price': 3.55, 'electricity_rate': 0.10},
    
    # Nebraska
    '68101': {'state': 'NE', 'geography_type': 'Urban', 'fuel_price': 3.30, 'electricity_rate': 0.09},
    '68502': {'state': 'NE', 'geography_type': 'Suburban', 'fuel_price': 3.25, 'electricity_rate': 0.09},
    
    # Nevada
    '89101': {'state': 'NV', 'geography_type': 'Urban', 'fuel_price': 4.05, 'electricity_rate': 0.11},
    '89501': {'state': 'NV', 'geography_type': 'Suburban', 'fuel_price': 4.00, 'electricity_rate': 0.11},
    
    # New Hampshire
    '03101': {'state': 'NH', 'geography_type': 'Urban', 'fuel_price': 3.65, 'electricity_rate': 0.16},
    '03301': {'state': 'NH', 'geography_type': 'Suburban', 'fuel_price': 3.60, 'electricity_rate': 0.15},
    
    # New Jersey
    '07101': {'state': 'NJ', 'geography_type': 'Urban', 'fuel_price': 3.70, 'electricity_rate': 0.14},
    '07302': {'state': 'NJ', 'geography_type': 'Urban', 'fuel_price': 3.75, 'electricity_rate': 0.14},
    '08701': {'state': 'NJ', 'geography_type': 'Suburban', 'fuel_price': 3.65, 'electricity_rate': 0.13},
    
    # New Mexico
    '87101': {'state': 'NM', 'geography_type': 'Urban', 'fuel_price': 3.40, 'electricity_rate': 0.12},
    '87501': {'state': 'NM', 'geography_type': 'Suburban', 'fuel_price': 3.35, 'electricity_rate': 0.11},
    
    # New York - NYC and State
    '10001': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.95, 'electricity_rate': 0.16},
    '10002': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.95, 'electricity_rate': 0.16},
    '10003': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.95, 'electricity_rate': 0.16},
    '10004': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.95, 'electricity_rate': 0.16},
    '10005': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.95, 'electricity_rate': 0.16},
    '11201': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.85, 'electricity_rate': 0.15},
    '11211': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.85, 'electricity_rate': 0.15},
    '10301': {'state': 'NY', 'geography_type': 'Suburban', 'fuel_price': 3.80, 'electricity_rate': 0.15},
    '12345': {'state': 'NY', 'geography_type': 'Suburban', 'fuel_price': 3.75, 'electricity_rate': 0.14},
    '14201': {'state': 'NY', 'geography_type': 'Urban', 'fuel_price': 3.70, 'electricity_rate': 0.14},
    '13201': {'state': 'NY', 'geography_type': 'Suburban', 'fuel_price': 3.65, 'electricity_rate': 0.13},
    
    # North Carolina
    '27601': {'state': 'NC', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.10},
    '28201': {'state': 'NC', 'geography_type': 'Urban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    '27401': {'state': 'NC', 'geography_type': 'Suburban', 'fuel_price': 3.25, 'electricity_rate': 0.09},
    
    # North Dakota
    '58101': {'state': 'ND', 'geography_type': 'Urban', 'fuel_price': 3.25, 'electricity_rate': 0.09},
    '58501': {'state': 'ND', 'geography_type': 'Suburban', 'fuel_price': 3.20, 'electricity_rate': 0.09},
    
    # Ohio
    '44101': {'state': 'OH', 'geography_type': 'Urban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    '44102': {'state': 'OH', 'geography_type': 'Urban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    '45201': {'state': 'OH', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.10},
    '43201': {'state': 'OH', 'geography_type': 'Urban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    
    # Oklahoma
    '73101': {'state': 'OK', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.10},
    '74101': {'state': 'OK', 'geography_type': 'Urban', 'fuel_price': 3.10, 'electricity_rate': 0.09},
    
    # Oregon
    '97201': {'state': 'OR', 'geography_type': 'Urban', 'fuel_price': 4.10, 'electricity_rate': 0.09},
    '97301': {'state': 'OR', 'geography_type': 'Suburban', 'fuel_price': 4.05, 'electricity_rate': 0.09},
    
    # Pennsylvania
    '19101': {'state': 'PA', 'geography_type': 'Urban', 'fuel_price': 3.70, 'electricity_rate': 0.13},
    '19102': {'state': 'PA', 'geography_type': 'Urban', 'fuel_price': 3.70, 'electricity_rate': 0.13},
    '15201': {'state': 'PA', 'geography_type': 'Urban', 'fuel_price': 3.60, 'electricity_rate': 0.12},
    '17101': {'state': 'PA', 'geography_type': 'Suburban', 'fuel_price': 3.55, 'electricity_rate': 0.12},
    
    # Rhode Island
    '02901': {'state': 'RI', 'geography_type': 'Urban', 'fuel_price': 3.75, 'electricity_rate': 0.18},
    '02840': {'state': 'RI', 'geography_type': 'Suburban', 'fuel_price': 3.70, 'electricity_rate': 0.17},
    
    # South Carolina
    '29201': {'state': 'SC', 'geography_type': 'Urban', 'fuel_price': 3.25, 'electricity_rate': 0.11},
    '29401': {'state': 'SC', 'geography_type': 'Suburban', 'fuel_price': 3.20, 'electricity_rate': 0.10},
    
    # South Dakota
    '57101': {'state': 'SD', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.10},
    '57701': {'state': 'SD', 'geography_type': 'Suburban', 'fuel_price': 3.30, 'electricity_rate': 0.10},
    
    # Tennessee
    '37201': {'state': 'TN', 'geography_type': 'Urban', 'fuel_price': 3.20, 'electricity_rate': 0.10},
    '38101': {'state': 'TN', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.09},
    '37402': {'state': 'TN', 'geography_type': 'Suburban', 'fuel_price': 3.10, 'electricity_rate': 0.09},
    
    # Texas - Major Cities
    '75201': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.25, 'electricity_rate': 0.11},
    '75202': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.25, 'electricity_rate': 0.11},
    '75204': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.25, 'electricity_rate': 0.11},
    '78701': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.12},
    '78702': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.35, 'electricity_rate': 0.12},
    '77001': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.20, 'electricity_rate': 0.10},
    '77002': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.20, 'electricity_rate': 0.10},
    '76101': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.15, 'electricity_rate': 0.09},
    '78201': {'state': 'TX', 'geography_type': 'Urban', 'fuel_price': 3.10, 'electricity_rate': 0.09},
    '79901': {'state': 'TX', 'geography_type': 'Suburban', 'fuel_price': 3.05, 'electricity_rate': 0.09},
    
    # Utah
    '84101': {'state': 'UT', 'geography_type': 'Urban', 'fuel_price': 3.75, 'electricity_rate': 0.09},
    '84601': {'state': 'UT', 'geography_type': 'Suburban', 'fuel_price': 3.70, 'electricity_rate': 0.09},
    
    # Vermont
    '05401': {'state': 'VT', 'geography_type': 'Suburban', 'fuel_price': 3.70, 'electricity_rate': 0.15},
    '05601': {'state': 'VT', 'geography_type': 'Suburban', 'fuel_price': 3.65, 'electricity_rate': 0.15},
    
    # Virginia
    '23219': {'state': 'VA', 'geography_type': 'Urban', 'fuel_price': 3.45, 'electricity_rate': 0.11},
    '22101': {'state': 'VA', 'geography_type': 'Suburban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    '23451': {'state': 'VA', 'geography_type': 'Suburban', 'fuel_price': 3.35, 'electricity_rate': 0.10},
    
    # Washington
    '98101': {'state': 'WA', 'geography_type': 'Urban', 'fuel_price': 4.25, 'electricity_rate': 0.08},
    '98102': {'state': 'WA', 'geography_type': 'Urban', 'fuel_price': 4.25, 'electricity_rate': 0.08},
    '98103': {'state': 'WA', 'geography_type': 'Urban', 'fuel_price': 4.25, 'electricity_rate': 0.08},
    '98001': {'state': 'WA', 'geography_type': 'Suburban', 'fuel_price': 4.15, 'electricity_rate': 0.07},
    '99201': {'state': 'WA', 'geography_type': 'Suburban', 'fuel_price': 4.10, 'electricity_rate': 0.07},
    
    # West Virginia
    '25301': {'state': 'WV', 'geography_type': 'Urban', 'fuel_price': 3.40, 'electricity_rate': 0.10},
    '26501': {'state': 'WV', 'geography_type': 'Suburban', 'fuel_price': 3.35, 'electricity_rate': 0.10},
    
    # Wisconsin
    '53201': {'state': 'WI', 'geography_type': 'Urban', 'fuel_price': 3.45, 'electricity_rate': 0.12},
    '53703': {'state': 'WI', 'geography_type': 'Suburban', 'fuel_price': 3.40, 'electricity_rate': 0.11},
    
    # Wyoming
    '82001': {'state': 'WY', 'geography_type': 'Suburban', 'fuel_price': 3.50, 'electricity_rate': 0.10},
    '82601': {'state': 'WY', 'geography_type': 'Rural', 'fuel_price': 3.45, 'electricity_rate': 0.10},
}

# State-based fuel price averages (fallback when ZIP not in database)
STATE_FUEL_PRICES = {
    'AL': 3.20, 'AK': 4.15, 'AZ': 3.85, 'AR': 3.10, 'CA': 4.65, 'CO': 3.50, 'CT': 3.75,
    'DE': 3.45, 'FL': 3.40, 'GA': 3.25, 'HI': 4.95, 'ID': 3.65, 'IL': 3.60, 'IN': 3.35,
    'IA': 3.25, 'KS': 3.15, 'KY': 3.30, 'LA': 3.05, 'ME': 3.70, 'MD': 3.55, 'MA': 3.80,
    'MI': 3.50, 'MN': 3.45, 'MS': 3.10, 'MO': 3.20, 'MT': 3.60, 'NE': 3.30, 'NV': 4.05,
    'NH': 3.65, 'NJ': 3.70, 'NM': 3.40, 'NY': 3.85, 'NC': 3.35, 'ND': 3.25, 'OH': 3.35,
    'OK': 3.15, 'OR': 4.10, 'PA': 3.65, 'RI': 3.75, 'SC': 3.25, 'SD': 3.35, 'TN': 3.20,
    'TX': 3.25, 'UT': 3.75, 'VT': 3.70, 'VA': 3.45, 'WA': 4.20, 'WV': 3.40, 'WI': 3.45, 'WY': 3.50
}

# State-based electricity rates (cents per kWh)
STATE_ELECTRICITY_RATES = {
    'AL': 0.11, 'AK': 0.22, 'AZ': 0.12, 'AR': 0.09, 'CA': 0.17, 'CO': 0.11, 'CT': 0.18,
    'DE': 0.12, 'FL': 0.11, 'GA': 0.10, 'HI': 0.28, 'ID': 0.08, 'IL': 0.12, 'IN': 0.11,
    'IA': 0.10, 'KS': 0.11, 'KY': 0.09, 'LA': 0.08, 'ME': 0.14, 'MD': 0.13, 'MA': 0.19,
    'MI': 0.11, 'MN': 0.11, 'MS': 0.10, 'MO': 0.10, 'MT': 0.10, 'NE': 0.09, 'NV': 0.11,
    'NH': 0.16, 'NJ': 0.14, 'NM': 0.12, 'NY': 0.15, 'NC': 0.10, 'ND': 0.09, 'OH': 0.11,
    'OK': 0.10, 'OR': 0.09, 'PA': 0.12, 'RI': 0.18, 'SC': 0.11, 'SD': 0.10, 'TN': 0.10,
    'TX': 0.10, 'UT': 0.09, 'VT': 0.15, 'VA': 0.11, 'WA': 0.08, 'WV': 0.10, 'WI': 0.12, 'WY': 0.10
}

# Comprehensive ZIP code range mapping for state determination
ZIP_CODE_RANGES = {
    'AL': [(35000, 36999)],
    'AK': [(99500, 99999)],
    'AZ': [(85000, 86599)],
    'AR': [(71600, 72999), (75502, 75502)],
    'CA': [(90000, 96199)],
    'CO': [(80000, 81699)],
    'CT': [(6000, 6999)],
    'DE': [(19700, 19999)],
    'FL': [(32000, 34999)],
    'GA': [(30000, 31999), (39800, 39999)],
    'HI': [(96700, 96899)],
    'ID': [(83200, 83899)],
    'IL': [(60000, 62999)],
    'IN': [(46000, 47999)],
    'IA': [(50000, 52899)],
    'KS': [(66000, 67999)],
    'KY': [(40000, 42799)],
    'LA': [(70000, 71499)],
    'ME': [(3900, 4999)],
    'MD': [(20600, 21999)],
    'MA': [(1000, 2799)],
    'MI': [(48000, 49999)],
    'MN': [(55000, 56799)],
    'MS': [(38600, 39799)],
    'MO': [(63000, 65999)],
    'MT': [(59000, 59999)],
    'NE': [(68000, 69399)],
    'NV': [(89000, 89899)],
    'NH': [(3000, 3899)],
    'NJ': [(7000, 8999)],
    'NM': [(87000, 88499)],
    'NY': [(10000, 14999)],
    'NC': [(27000, 28999)],
    'ND': [(58000, 58899)],
    'OH': [(43000, 45999)],
    'OK': [(73000, 74999)],
    'OR': [(97000, 97999)],
    'PA': [(15000, 19699)],
    'RI': [(2800, 2999)],
    'SC': [(29000, 29999)],
    'SD': [(57000, 57799)],
    'TN': [(37000, 38599)],
    'TX': [(73300, 73399), (75000, 79999), (77000, 77999), (78000, 79999)],
    'UT': [(84000, 84799)],
    'VT': [(5000, 5999)],
    'VA': [(20000, 24699)],
    'WA': [(98000, 99499)],
    'WV': [(24700, 26899)],
    'WI': [(53000, 54999)],
    'WY': [(82000, 83199)]
}

def validate_zip_code(zip_code: str) -> bool:
    """Validate ZIP code format"""
    if not zip_code:
        return False
    
    # Check if it's exactly 5 digits
    pattern = r'^\d{5}$'
    return bool(re.match(pattern, zip_code))

def lookup_zip_code_data(zip_code: str) -> Optional[Dict[str, Any]]:
    """Lookup location data based on ZIP code"""
    if not validate_zip_code(zip_code):
        return None
    
    # First try exact lookup
    if zip_code in ZIP_CODE_DATABASE:
        return ZIP_CODE_DATABASE[zip_code].copy()
    
    # Fallback: try to determine state from ZIP code ranges
    state = determine_state_from_zip(zip_code)
    if state:
        geography_type = get_geography_type_from_zip(zip_code)
        return {
            'state': state,
            'geography_type': geography_type,
            'fuel_price': STATE_FUEL_PRICES.get(state, 3.50),
            'electricity_rate': STATE_ELECTRICITY_RATES.get(state, 0.12)
        }
    
    return None

def determine_state_from_zip(zip_code: str) -> Optional[str]:
    """Determine state from ZIP code using comprehensive ranges"""
    if not validate_zip_code(zip_code):
        return None
    
    zip_int = int(zip_code)
    
    for state, ranges in ZIP_CODE_RANGES.items():
        for start, end in ranges:
            if start <= zip_int <= end:
                return state
    
    return None

def get_geography_type_from_zip(zip_code: str) -> str:
    """Determine geography type from ZIP code (enhanced logic)"""
    if not validate_zip_code(zip_code):
        return 'Suburban'
    
    zip_int = int(zip_code)
    
    # Major urban centers (comprehensive list)
    urban_zip_ranges = [
        # New York City
        (10001, 10299), (11201, 11299), (11101, 11199),
        # Los Angeles
        (90001, 90099), (90201, 90299), (91401, 91499),
        # Chicago
        (60601, 60661), (60007, 60199),
        # Houston
        (77001, 77099), (77201, 77299),
        # Phoenix
        (85001, 85099), (85201, 85299),
        # Philadelphia
        (19101, 19199), (19201, 19299),
        # San Antonio
        (78201, 78299),
        # San Diego
        (92101, 92199),
        # Dallas
        (75201, 75299),
        # San Jose/Silicon Valley
        (95101, 95199), (94301, 94399),
        # Austin
        (78701, 78799),
        # Jacksonville
        (32201, 32299),
        # San Francisco
        (94102, 94199),
        # Columbus
        (43201, 43299),
        # Charlotte
        (28201, 28299),
        # Fort Worth
        (76101, 76199),
        # Indianapolis
        (46201, 46299),
        # Seattle
        (98101, 98199),
        # Denver
        (80201, 80299),
        # Washington DC
        (20001, 20099),
        # Boston
        (2101, 2199), (2201, 2299),
        # El Paso
        (79901, 79999),
        # Detroit
        (48201, 48299),
        # Nashville
        (37201, 37299),
        # Portland
        (97201, 97299),
        # Memphis
        (38101, 38199),
        # Oklahoma City
        (73101, 73199),
        # Las Vegas
        (89101, 89199),
        # Louisville
        (40201, 40299),
        # Baltimore
        (21201, 21299),
        # Milwaukee
        (53201, 53299),
        # Albuquerque
        (87101, 87199),
        # Tucson
        (85701, 85799),
        # Fresno
        (93701, 93799),
        # Sacramento
        (95801, 95899),
        # Kansas City
        (64101, 64199),
        # Mesa
        (85201, 85299),
        # Atlanta
        (30301, 30399),
        # Colorado Springs
        (80901, 80999),
        # Omaha
        (68101, 68199),
        # Raleigh
        (27601, 27699),
        # Miami
        (33101, 33199),
        # Cleveland
        (44101, 44199),
        # Tulsa
        (74101, 74199),
        # Minneapolis
        (55401, 55499),
        # Wichita
        (67201, 67299),
        # New Orleans
        (70112, 70199)
    ]
    
    # Check if ZIP is in urban range
    for start, end in urban_zip_ranges:
        if start <= zip_int <= end:
            return 'Urban'
    
    # Rural indicators - very low population density areas
    rural_zip_patterns = [
        # Alaska rural areas
        (99501, 99999),
        # Montana rural
        (59001, 59099),
        # Wyoming rural
        (82001, 82999),
        # North Dakota rural
        (58001, 58099),
        # South Dakota rural
        (57001, 57099),
        # Nevada rural
        (89001, 89099),
        # Idaho rural
        (83001, 83199),
        # Vermont rural
        (5001, 5099),
        # Maine rural
        (4001, 4199),
        # West Virginia rural
        (24701, 25999)
    ]
    
    # Check if ZIP is in rural range
    for start, end in rural_zip_patterns:
        if start <= zip_int <= end:
            return 'Rural'
    
    # Default to suburban for most ZIP codes
    return 'Suburban'

def get_fuel_price_estimate(zip_code: str, state: str = '') -> float:
    """Get estimated fuel price for location"""
    # Try ZIP code lookup first
    zip_data = lookup_zip_code_data(zip_code)
    if zip_data:
        return zip_data.get('fuel_price', 3.50)
    
    # Fall back to state average
    if state in STATE_FUEL_PRICES:
        return STATE_FUEL_PRICES[state]
    
    # National average fallback
    return 3.50

def get_electricity_rate_estimate(zip_code: str, state: str = '') -> float:
    """Get estimated electricity rate for location"""
    # Try ZIP code lookup first
    zip_data = lookup_zip_code_data(zip_code)
    if zip_data:
        return zip_data.get('electricity_rate', 0.12)
    
    # Fall back to state average
    if state in STATE_ELECTRICITY_RATES:
        return STATE_ELECTRICITY_RATES[state]
    
    # National average fallback
    return 0.12

def validate_and_lookup_location(zip_code: str) -> Dict[str, Any]:
    """Comprehensive location validation and lookup"""
    result = {
        'is_valid': False,
        'zip_code': zip_code,
        'state': '',
        'geography_type': '',
        'fuel_price': 3.50,
        'electricity_rate': 0.12,
        'error_message': ''
    }
    
    # Validate format
    if not validate_zip_code(zip_code):
        result['error_message'] = 'Invalid ZIP code format. Please enter 5 digits.'
        return result
    
    # Lookup data
    zip_data = lookup_zip_code_data(zip_code)
    if zip_data:
        result.update({
            'is_valid': True,
            'state': zip_data['state'],
            'geography_type': zip_data['geography_type'],
            'fuel_price': zip_data['fuel_price'],
            'electricity_rate': zip_data['electricity_rate']
        })
    else:
        # Try to determine state at least
        state = determine_state_from_zip(zip_code)
        if state:
            result.update({
                'is_valid': True,
                'state': state,
                'geography_type': get_geography_type_from_zip(zip_code),
                'fuel_price': STATE_FUEL_PRICES.get(state, 3.50),
                'electricity_rate': STATE_ELECTRICITY_RATES.get(state, 0.12),
                'error_message': 'ZIP code recognized but detailed data unavailable. Using state averages.'
            })
        else:
            result['error_message'] = 'ZIP code not recognized. Please verify and try again.'
    
    return result

def get_regional_cost_multiplier(geography_type: str, state: str = '') -> float:
    """Get regional cost multiplier for maintenance and other costs"""
    base_multipliers = {
        'urban': 1.15,      # 15% higher costs in urban areas
        'suburban': 1.0,    # Baseline
        'rural': 0.85       # 15% lower costs in rural areas
    }
    
    # State-specific adjustments
    high_cost_states = ['CA', 'NY', 'HI', 'MA', 'CT', 'NJ', 'AK']
    low_cost_states = ['MS', 'AL', 'AR', 'WV', 'OK', 'KS', 'ND', 'SD']
    
    multiplier = base_multipliers.get(geography_type.lower(), 1.0)
    
    if state in high_cost_states:
        multiplier *= 1.1  # Additional 10% for high-cost states
    elif state in low_cost_states:
        multiplier *= 0.9  # 10% discount for low-cost states
    
    return multiplier

def get_zip_code_coverage_stats() -> Dict[str, Any]:
    """Get statistics about ZIP code database coverage"""
    
    states_covered = set()
    urban_count = 0
    suburban_count = 0
    rural_count = 0
    
    for zip_code, data in ZIP_CODE_DATABASE.items():
        states_covered.add(data['state'])
        geography = data['geography_type'].lower()
        if geography == 'urban':
            urban_count += 1
        elif geography == 'suburban':
            suburban_count += 1
        elif geography == 'rural':
            rural_count += 1
    
    return {
        'total_zip_codes': len(ZIP_CODE_DATABASE),
        'states_covered': len(states_covered),
        'coverage_by_geography': {
            'urban': urban_count,
            'suburban': suburban_count,
            'rural': rural_count
        },
        'states_list': sorted(list(states_covered)),
        'coverage_percentage': (len(states_covered) / 50) * 100  # 50 states
    }

def search_nearby_zip_codes(zip_code: str, radius: int = 10) -> List[Dict[str, Any]]:
    """Search for nearby ZIP codes with data (simplified implementation)"""
    if not validate_zip_code(zip_code):
        return []
    
    zip_int = int(zip_code)
    nearby_zips = []
    
    # Search within radius for ZIP codes in database
    for test_zip in range(max(10000, zip_int - radius), min(99999, zip_int + radius + 1)):
        test_zip_str = f"{test_zip:05d}"
        if test_zip_str in ZIP_CODE_DATABASE:
            data = ZIP_CODE_DATABASE[test_zip_str].copy()
            data['zip_code'] = test_zip_str
            data['distance'] = abs(test_zip - zip_int)
            nearby_zips.append(data)
    
    # Sort by distance
    nearby_zips.sort(key=lambda x: x['distance'])
    
    return nearby_zips

# Test function
def test_zip_code_lookup():
    """Test the ZIP code lookup functionality with comprehensive examples"""
    test_zips = [
        '90210',  # Beverly Hills, CA
        '10001',  # Manhattan, NY
        '77001',  # Houston, TX
        '30301',  # Atlanta, GA
        '99999',  # Alaska (invalid but in range)
        '12345',  # Generic test
        '60601',  # Chicago, IL
        '94102',  # San Francisco, CA
        '33101',  # Miami, FL
        '02101',  # Boston, MA
        '98101',  # Seattle, WA
        '80201',  # Denver, CO
        '75201',  # Dallas, TX
        '85001',  # Phoenix, AZ
        '19101',  # Philadelphia, PA
    ]
    
    print("Comprehensive ZIP Code Lookup Test:")
    print("=" * 60)
    
    for zip_code in test_zips:
        result = validate_and_lookup_location(zip_code)
        print(f"\nZIP: {zip_code}")
        print(f"  Valid: {result['is_valid']}")
        print(f"  State: {result['state']}")
        print(f"  Geography: {result['geography_type']}")
        print(f"  Fuel Price: ${result['fuel_price']:.2f}")
        print(f"  Electricity: ${result['electricity_rate']:.3f}/kWh")
        if result['error_message']:
            print(f"  Message: {result['error_message']}")
        
        # Test regional multiplier
        multiplier = get_regional_cost_multiplier(result['geography_type'], result['state'])
        print(f"  Cost Multiplier: {multiplier:.2f}x")
    
    print("\n" + "=" * 60)
    
    # Display coverage statistics
    coverage = get_zip_code_coverage_stats()
    print(f"\nDatabase Coverage Statistics:")
    print(f"Total ZIP codes: {coverage['total_zip_codes']}")
    print(f"States covered: {coverage['states_covered']}/50 ({coverage['coverage_percentage']:.1f}%)")
    print(f"Urban ZIPs: {coverage['coverage_by_geography']['urban']}")
    print(f"Suburban ZIPs: {coverage['coverage_by_geography']['suburban']}")
    print(f"Rural ZIPs: {coverage['coverage_by_geography']['rural']}")
    print(f"States: {', '.join(coverage['states_list'][:10])}...")

if __name__ == "__main__":
    test_zip_code_lookup()