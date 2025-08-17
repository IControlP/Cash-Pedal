# Vehicle Total Cost of Ownership Calculator

A comprehensive Streamlit-based web application for calculating and comparing vehicle ownership costs over time. Features advanced multi-vehicle comparison, lease vs purchase analysis, and ZIP code-based cost adjustments.

## Features

### Core Functionality
- **Single Vehicle Analysis**: Calculate TCO for individual vehicles
- **Multi-Vehicle Comparison**: Compare up to 5 vehicles simultaneously  
- **Lease vs Purchase**: Support for both financing options
- **ZIP Code Integration**: Auto-populate location-based costs
- **Interactive Visualizations**: Charts and graphs for cost analysis

### Advanced Features
- **Geographic Cost Adjustments**: Regional fuel prices and cost multipliers
- **Automated Recommendations**: AI-powered pros/cons analysis
- **Affordability Assessment**: Budget compatibility analysis
- **Export Capabilities**: PDF and CSV report generation
- **Mobile Responsive**: Works on desktop and mobile browsers

## Installation

1. **Clone/Download the Project**
   ```bash
   # Create project directory
   mkdir vehicle_tco_calculator
   cd vehicle_tco_calculator
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Project Structure**
   ```
   vehicle_tco_calculator/
   ├── main.py                     # Main application entry point
   ├── requirements.txt            # Python dependencies
   ├── README.md                   # This file
   ├── ui/
   │   ├── input_forms.py         # User input forms
   │   ├── calculator_display.py   # Single vehicle calculator UI
   │   └── comparison_display.py   # Multi-vehicle comparison UI
   ├── models/
   │   ├── depreciation/
   │   │   └── enhanced_depreciation.py
   │   ├── maintenance/
   │   │   └── maintenance_utils.py
   │   ├── insurance/
   │   │   └── advanced_insurance.py
   │   └── fuel/
   │       ├── fuel_utils.py
   │       └── electric_vehicle_utils.py
   ├── services/
   │   ├── prediction_service.py   # Main TCO calculation orchestrator
   │   ├── financial_analysis.py   # Financial calculations
   │   ├── comparison_service.py   # Multi-vehicle comparison
   │   └── recommendation_engine.py
   ├── data/
   │   ├── vehicle_database.py     # Vehicle data interface
   │   ├── vehicle_database_c.py   # Chevrolet data
   │   ├── vehicle_database_h.py   # Honda/Hyundai data
   │   └── vehicle_database_r.py   # Ram data
   └── utils/
       ├── session_manager.py      # Session state management
       └── zip_code_utils.py       # ZIP code lookup utilities
   ```

## Usage

### Starting the Application
```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Single Vehicle Calculator

1. **Vehicle Selection**
   - Choose manufacturer, model, year, and trim
   - Select transaction type (Purchase or Lease)

2. **Location Information**
   - Enter ZIP code for automatic regional cost detection
   - System auto-populates state, geography type, and fuel prices

3. **Personal Information**
   - Enter age, income, and driving patterns
   - Specify annual mileage and driving style

4. **Financial Parameters**
   - For purchases: loan amount, interest rate, loan term
   - For leases: monthly payment, mileage limit, lease term

5. **Calculate TCO**
   - Click "Calculate TCO" to generate results
   - View detailed cost breakdown and visualizations
   - Add to comparison for multi-vehicle analysis

### Using the Multi-Vehicle Comparison

1. **Add Vehicles**
   - Use Single Vehicle Calculator to analyze vehicles
   - Click "Add to Comparison" for each vehicle
   - Support for mixing lease and purchase options

2. **View Comparison**
   - Navigate to "Multi-Vehicle Comparison"
   - See side-by-side cost analysis
   - Interactive charts and rankings

3. **Get Recommendations**
   - Automated pros/cons for each vehicle
   - Best choice by different criteria
   - Detailed decision factors

4. **Export Results**
   - Download comparison reports
   - PDF and CSV formats available

## Configuration

### Vehicle Database
The application includes sample data for:
- **Chevrolet**: Silverado, Colorado models (2014-2025)
- **Honda**: Civic, Pilot, Passport, Ridgeline models  
- **Hyundai**: Elantra, Santa Fe, Genesis models
- **Ram**: 1500 models (2014-2025)

To add more manufacturers:
1. Create new database file: `data/vehicle_database_[letter].py`
2. Follow existing format with make/model/year/trim/pricing data
3. Update `data/vehicle_database.py` to include new manufacturer

### ZIP Code Data
The application includes sample ZIP code mappings for major metro areas. To expand:
1. Edit `utils/zip_code_utils.py`
2. Add ZIP codes to `ZIP_CODE_DATABASE` dictionary
3. Include state, geography type, fuel price, and electricity rate

### Regional Cost Adjustments
Modify cost multipliers in `utils/zip_code_utils.py`:
- Urban areas: 15% higher costs
- Rural areas: 15% lower costs  
- State-specific adjustments for high/low cost regions

## Technical Architecture

### Model Classes
- **EnhancedDepreciationModel**: Market-based depreciation with brand adjustments
- **MaintenanceCalculator**: Service intervals and wear-based costs
- **AdvancedInsuranceCalculator**: State-specific premium calculations
- **FuelCostCalculator**: MPG-based fuel cost analysis
- **EVCostCalculator**: Electric vehicle energy costs

### Service Classes
- **PredictionService**: Orchestrates all TCO calculations
- **FinancialAnalysisService**: Loan payments and affordability analysis
- **ComparisonService**: Multi-vehicle comparison engine
- **RecommendationEngine**: Automated insights and recommendations

### Data Management
- **SessionManager**: Streamlit session state management
- **VehicleDatabase**: Unified interface to manufacturer data
- **ZipCodeUtils**: Geographic data lookup and validation

## Customization

### Adding New Calculation Models
1. Create new model in appropriate `models/` subdirectory
2. Follow existing interface patterns
3. Update `PredictionService` to integrate new model

### Modifying UI Components
- Edit files in `ui/` directory
- Use Streamlit components and Plotly for visualizations
- Follow responsive design patterns

### Extending Database
- Add new manufacturer data files
- Update vehicle characteristics in `get_vehicle_characteristics()`
- Expand ZIP code coverage as needed

## Performance Considerations

- Calculations complete in < 5 seconds for single vehicle
- Comparison processing < 2 seconds for up to 5 vehicles
- Session state maintains user data during browser session
- No permanent data storage (privacy-compliant)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers supported

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd vehicle_tco_calculator
   python -c "import streamlit; print('Streamlit installed')"
   ```

2. **ZIP Code Not Found**
   - System falls back to manual state entry
   - Add ZIP codes to database as needed

3. **Vehicle Data Missing**
   - Check manufacturer/model spelling
   - Verify year is within production range
   - Add missing vehicles to database

4. **Calculation Errors**
   - Verify all required fields are completed
   - Check for reasonable input values
   - Review error messages for specific issues

### Debug Mode
Set environment variable for detailed logging:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run main.py
```

## Contributing

To extend the application:

1. **Add New Features**
   - Follow existing code patterns
   - Update this README with new functionality
   - Test thoroughly before deployment

2. **Improve Calculations**
   - Enhance depreciation models with more data
   - Add more sophisticated insurance calculations
   - Integrate real-time fuel price APIs

3. **Expand Database**
   - Add more manufacturers and models
   - Include electric vehicle efficiency data
   - Expand geographic coverage

## License

This project is provided as-is for educational and personal use. 

## Support

For issues or questions:
1. Check this README for common solutions
2. Review code comments for implementation details
3. Test with sample data to isolate issues

---

**Vehicle Total Cost of Ownership Calculator v1.02.2**  
*Comprehensive vehicle financial analysis made simple*