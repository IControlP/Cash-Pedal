"""
Multi-Vehicle Comparison Display Interface
Handles the display of vehicle comparisons, rankings, and recommendations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

def display_comparison():
    """Display the multi-vehicle comparison interface"""
    
    st.header("⚖️ Multi-Vehicle Comparison")
    
    # Check if we have vehicles to compare
    if not hasattr(st.session_state, 'comparison_vehicles') or not st.session_state.comparison_vehicles:
        display_empty_comparison()
        return
    
    vehicle_count = len(st.session_state.comparison_vehicles)
    
    # Display current vehicles in comparison
    display_comparison_summary()
    
    if vehicle_count >= 2:
        # Show comparison results
        display_comparison_results()
    else:
        st.info("Add at least 2 vehicles to see comparison results.")
        st.markdown("💡 **Tip:** Use the Single Vehicle Calculator to analyze and add vehicles to comparison.")

def display_empty_comparison():
    """Display interface when no vehicles are in comparison"""
    
    st.info("🚗 No vehicles in comparison yet.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### How to Add Vehicles:
        1. Go to **Single Vehicle Calculator**
        2. Configure a vehicle and calculate TCO
        3. Click **"Add to Comparison"**
        4. Repeat for additional vehicles (up to 5)
        """)
    
    with col2:
        st.markdown("""
        ### Comparison Features:
        - ⚖️ Side-by-side cost analysis
        - 📊 Interactive visualizations
        - 💡 Automated recommendations
        - 📄 Exportable reports
        - 🔄 Lease vs Purchase mixing
        """)
    
    # Quick add section (if we had a simplified form)
    with st.expander("🚀 Quick Add Vehicle", expanded=False):
        st.markdown("*Quick vehicle addition coming in future update*")
        st.info("For now, please use the Single Vehicle Calculator to add vehicles.")

def display_comparison_summary():
    """Display summary of vehicles currently in comparison"""
    
    st.subheader("📋 Vehicles in Comparison")
    
    vehicles = st.session_state.comparison_vehicles
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vehicles", len(vehicles))
    
    with col2:
        lease_count = sum(1 for v in vehicles if v.get('transaction_type', '').lower() == 'lease')
        st.metric("Leases", lease_count)
    
    with col3:
        purchase_count = len(vehicles) - lease_count
        st.metric("Purchases", purchase_count)
    
    with col4:
        if len(vehicles) >= 2:
            st.success("✅ Ready to Compare")
        else:
            st.warning("⏳ Need 1+ More")
    
    # List current vehicles
    for i, vehicle in enumerate(vehicles):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            price = vehicle.get('trim_msrp', 0)
            transaction = vehicle.get('transaction_type', 'Unknown')
            vehicle_name = f"{vehicle.get('year', '')} {vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('trim', '')}"
            
            if transaction.lower() == 'lease':
                monthly = vehicle.get('lease_monthly_payment', 0)
                st.write(f"🟢 **{vehicle_name}** ({transaction}) - ${monthly:,.0f}/month")
            else:
                st.write(f"🟢 **{vehicle_name}** ({transaction}) - ${price:,.0f}")
        
        with col2:
            if st.button("🗑️ Remove", key=f"remove_{i}"):
                st.session_state.comparison_vehicles.pop(i)
                st.rerun()

def display_comparison_results():
    """Display detailed comparison results"""
    
    vehicles = st.session_state.comparison_vehicles
    
    # Import comparison service here to avoid circular imports
    try:
        from services.comparison_service import ComparisonService
    except ImportError:
        # Fallback if comparison service is not available
        st.error("Comparison service not available. Please ensure all required modules are installed.")
        return
    
    comparison_service = ComparisonService()
    
    # Calculate comparison results
    with st.spinner("Generating comparison results..."):
        try:
            comparison_results = comparison_service.compare_vehicles(vehicles)
            
            # Get recommendations
            recommendations = comparison_service.get_vehicle_recommendations(comparison_results)
            
        except Exception as e:
            st.error(f"Error generating comparison: {str(e)}")
            st.error("Please check your vehicle configurations and try again.")
            return
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Refresh Comparison", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📄 Export Report", use_container_width=True):
            export_comparison_report(comparison_results, recommendations)
    
    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.comparison_vehicles = []
            st.rerun()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Executive Summary", 
        "📊 Cost Comparison", 
        "📈 Visualizations", 
        "💡 Recommendations"
    ])
    
    with tab1:
        display_executive_summary(comparison_results, recommendations)
    
    with tab2:
        display_cost_comparison_table(comparison_results)
    
    with tab3:
        display_comparison_visualizations(comparison_results)
    
    with tab4:
        display_recommendations_detailed(recommendations)

def display_executive_summary(comparison_results: Dict[str, Any], 
                             recommendations: Dict[str, Any]):
    """Display executive summary of comparison"""
    
    st.subheader("🏆 Executive Summary")
    
    # Winner announcement
    if comparison_results.get('best_overall'):
        best_vehicle = comparison_results['best_overall']
        
        st.success(f"""
        ### 🥇 **Best Overall Choice**
        **{best_vehicle['vehicle_name']}** ({best_vehicle['transaction_type']})
        
        **Annual Cost:** ${best_vehicle['annual_cost']:,.0f}  
        **Total Cost:** ${best_vehicle['total_cost']:,.0f}  
        **Affordability:** {'✅ Good' if best_vehicle.get('is_affordable', False) else '⚠️ Marginal'}
        """)
    
    # Quick comparison metrics
    st.markdown("#### 📊 Quick Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Vehicles Analyzed", 
            len(comparison_results.get('vehicles', [])),
            help="Total vehicles in comparison"
        )
    
    with col2:
        if comparison_results.get('cost_range'):
            cost_range = comparison_results['cost_range']
            st.metric(
                "Cost Range", 
                f"${cost_range:,.0f}",
                help="Difference between highest and lowest cost options"
            )
    
    with col3:
        if comparison_results.get('average_annual_cost'):
            avg_cost = comparison_results['average_annual_cost']
            st.metric(
                "Average Annual Cost", 
                f"${avg_cost:,.0f}",
                help="Average across all vehicles"
            )
    
    # Key insights
    st.markdown("#### 🔍 Key Insights")
    
    insights = recommendations.get('key_insights', [])
    if insights:
        for insight in insights[:5]:  # Show top 5 insights
            st.markdown(f"• {insight}")
    else:
        st.info("Detailed insights will appear here after analysis.")

def display_cost_comparison_table(comparison_results: Dict[str, Any]):
    """Display detailed cost comparison table"""
    
    st.subheader("📊 Detailed Cost Comparison")
    
    vehicles = comparison_results.get('vehicles', [])
    if not vehicles:
        st.warning("No comparison data available.")
        return
    
    # Create comparison DataFrame
    comparison_data = []
    
    for vehicle in vehicles:
        # Fix: Ensure we're using the correct annual cost, not total cost
        annual_cost = vehicle.get('annual_cost', 0)
        total_cost = vehicle.get('total_cost', 0)
        
        # Double-check: if annual cost seems too high (possibly total cost), recalculate
        analysis_years = vehicle.get('analysis_years', 5)
        if analysis_years > 0 and annual_cost > total_cost * 0.8:
            # This suggests annual_cost is actually total_cost, fix it
            annual_cost = total_cost / analysis_years
        
        # Calculate income percentage from raw results
        raw_results = vehicle.get('raw_results', {})
        affordability = raw_results.get('affordability', {})
        income_percentage = affordability.get('percentage_of_income', 0)
        
        # If not available, try to calculate from affordability score
        if income_percentage == 0:
            income_percentage = vehicle.get('affordability_score', 0)
        
        row = {
            'Vehicle': vehicle['vehicle_name'],
            'Type': vehicle['transaction_type'],
            'Total Cost': total_cost,
            'Annual Cost': annual_cost,
            'Monthly Cost': annual_cost / 12,
            'Cost per Mile': vehicle.get('cost_per_mile', 0),
            '% of Income': income_percentage,  # NEW: Income percentage
            'Affordable': '✅' if vehicle.get('is_affordable', False) else '⚠️'
        }
        
        # Add category breakdowns if available
        categories = vehicle.get('cost_categories', {})
        for category, amount in categories.items():
            row[category.replace('_', ' ').title()] = amount
        
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    
    # Format currency columns
    currency_columns = ['Total Cost', 'Annual Cost', 'Monthly Cost']
    for col in currency_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"${x:,.0f}")
    
    if 'Cost per Mile' in df.columns:
        df['Cost per Mile'] = df['Cost per Mile'].apply(lambda x: f"${x:.3f}")
    
    # Format percentage column
    if '% of Income' in df.columns:
        df['% of Income'] = df['% of Income'].apply(lambda x: f"{x:.1f}%" if x > 0 else "N/A")
    
    # Display table
    st.dataframe(df, use_container_width=True)
    
    # Enhanced ranking section with income percentage
    st.markdown("#### 🏅 Rankings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**By Total Cost:**")
        sorted_by_total = sorted(vehicles, key=lambda x: x['total_cost'])
        for i, vehicle in enumerate(sorted_by_total[:3]):
            emoji = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"{emoji} {vehicle['vehicle_name']}: ${vehicle['total_cost']:,.0f}")
    
    with col2:
        st.markdown("**By Annual Cost:**")
        # Fix annual cost for ranking too
        vehicles_with_fixed_annual = []
        for vehicle in vehicles:
            annual_cost = vehicle.get('annual_cost', 0)
            total_cost = vehicle.get('total_cost', 0)
            analysis_years = vehicle.get('analysis_years', 5)
            
            if analysis_years > 0 and annual_cost > total_cost * 0.8:
                annual_cost = total_cost / analysis_years
            
            vehicles_with_fixed_annual.append({
                **vehicle,
                'fixed_annual_cost': annual_cost
            })
        
        sorted_by_annual = sorted(vehicles_with_fixed_annual, key=lambda x: x['fixed_annual_cost'])
        for i, vehicle in enumerate(sorted_by_annual[:3]):
            emoji = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"{emoji} {vehicle['vehicle_name']}: ${vehicle['fixed_annual_cost']:,.0f}")
    
    with col3:
        st.markdown("**By Income Impact:**")
        # Sort by income percentage (lowest first = most affordable)
        vehicles_with_income = [v for v in vehicles if v.get('raw_results', {}).get('affordability', {}).get('percentage_of_income', 0) > 0]
        if vehicles_with_income:
            sorted_by_income = sorted(vehicles_with_income, 
                                    key=lambda x: x.get('raw_results', {}).get('affordability', {}).get('percentage_of_income', 100))
            for i, vehicle in enumerate(sorted_by_income[:3]):
                emoji = ["🥇", "🥈", "🥉"][i]
                income_pct = vehicle.get('raw_results', {}).get('affordability', {}).get('percentage_of_income', 0)
                st.markdown(f"{emoji} {vehicle['vehicle_name']}: {income_pct:.1f}%")
        else:
            st.info("Income data not available for ranking")

def display_comparison_visualizations(comparison_results: Dict[str, Any]):
    """Display comparison charts and visualizations - using line graphs with overlaid data points"""
    
    st.subheader("📈 Visual Analysis")
    
    vehicles = comparison_results.get('vehicles', [])
    if not vehicles:
        st.warning("No data available for visualization.")
        return
    
    # Fix annual costs in vehicles data
    fixed_vehicles = []
    for vehicle in vehicles:
        annual_cost = vehicle.get('annual_cost', 0)
        total_cost = vehicle.get('total_cost', 0)
        analysis_years = vehicle.get('analysis_years', 5)
        
        if analysis_years > 0 and annual_cost > total_cost * 0.8:
            annual_cost = total_cost / analysis_years
        
        fixed_vehicles.append({
            **vehicle,
            'fixed_annual_cost': annual_cost
        })
    
    # Prepare data for plotting
    vehicle_names = [v['vehicle_name'] for v in fixed_vehicles]
    total_costs = [v['total_cost'] for v in fixed_vehicles]
    annual_costs = [v['fixed_annual_cost'] for v in fixed_vehicles]
    transaction_types = [v['transaction_type'] for v in fixed_vehicles]
    
    # Color mapping for different vehicles
    colors = px.colors.qualitative.Set1[:len(fixed_vehicles)]
    
    # Total cost comparison - OVERLAID BAR CHART
    fig_total = go.Figure()
    
    # Create a simple category axis with cost values overlaid
    categories = ['Total Cost Comparison']
    
    for i, vehicle in enumerate(fixed_vehicles):
        fig_total.add_trace(go.Bar(
            x=categories,
            y=[vehicle['total_cost']],
            name=vehicle['vehicle_name'],
            marker_color=colors[i],
            text=f"${vehicle['total_cost']:,.0f}",
            textposition='auto',
            width=0.6  # Make bars narrower so they overlap better
        ))
    
    fig_total.update_layout(
        title="Total Cost Comparison - All Vehicles",
        xaxis_title="",
        yaxis_title="Total Cost ($)",
        height=400,
        barmode='group',  # Group bars side by side
        showlegend=True
    )
    
    st.plotly_chart(fig_total, use_container_width=True)
    
    # Annual cost comparison - OVERLAID BAR CHART
    fig_annual = go.Figure()
    
    for i, vehicle in enumerate(fixed_vehicles):
        fig_annual.add_trace(go.Bar(
            x=categories,
            y=[vehicle['fixed_annual_cost']],
            name=vehicle['vehicle_name'],
            marker_color=colors[i],
            text=f"${vehicle['fixed_annual_cost']:,.0f}",
            textposition='auto',
            width=0.6
        ))
    
    fig_annual.update_layout(
        title="Annual Cost Comparison - All Vehicles",
        xaxis_title="",
        yaxis_title="Annual Cost ($)",
        height=400,
        barmode='group',
        showlegend=True
    )
    
    st.plotly_chart(fig_annual, use_container_width=True)
    
    # Cost breakdown by category (if available) - STACKED BAR CHART
    if len(fixed_vehicles) > 0 and fixed_vehicles[0].get('cost_categories'):
        
        st.markdown("#### Cost Category Breakdown")
        
        # Create grouped bar chart for categories
        categories = list(fixed_vehicles[0]['cost_categories'].keys())
        
        fig_stack = go.Figure()
        
        colors_stack = px.colors.qualitative.Set3
        
        for i, category in enumerate(categories):
            category_values = []
            vehicle_labels = []
            
            for vehicle in fixed_vehicles:
                category_values.append(vehicle['cost_categories'].get(category, 0))
                vehicle_labels.append(vehicle['vehicle_name'])
            
            fig_stack.add_trace(go.Bar(
                name=category.replace('_', ' ').title(),
                x=vehicle_labels,
                y=category_values,
                marker_color=colors_stack[i % len(colors_stack)]
            ))
        
        fig_stack.update_layout(
            title="Cost Breakdown by Category - All Vehicles",
            xaxis_title="Vehicle",
            yaxis_title="Cost ($)",
            barmode='stack',
            height=500,
            xaxis={'categoryorder': 'total descending'}
        )
        
        st.plotly_chart(fig_stack, use_container_width=True)
    
    # Dot plot: Cost comparison with all metrics
    fig_dot = go.Figure()
    
    metrics = ['Total Cost', 'Annual Cost', 'Monthly Cost']
    
    for i, vehicle in enumerate(fixed_vehicles):
        y_values = [
            vehicle['total_cost'],
            vehicle['fixed_annual_cost'], 
            vehicle['fixed_annual_cost'] / 12
        ]
        
        fig_dot.add_trace(go.Scatter(
            x=metrics,
            y=y_values,
            mode='markers+lines+text',
            name=vehicle['vehicle_name'],
            text=[f"${val:,.0f}" for val in y_values],
            textposition="top center",
            marker=dict(size=12, color=colors[i]),
            line=dict(width=3, color=colors[i])
        ))
    
    fig_dot.update_layout(
        title="Multi-Metric Cost Comparison",
        xaxis_title="Cost Metric",
        yaxis_title="Cost ($)",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_dot, use_container_width=True)

def display_recommendations_detailed(recommendations: Dict[str, Any]):
    """Display detailed recommendations for each vehicle"""
    
    st.subheader("🎯 Detailed Recommendations")
    
    vehicle_recommendations = recommendations.get('vehicle_recommendations', {})
    
    if not vehicle_recommendations:
        st.info("Detailed recommendations will appear here after comparison analysis.")
        return
    
    # Display recommendations for each vehicle
    for vehicle_name, vehicle_rec in vehicle_recommendations.items():
        with st.expander(f"📝 {vehicle_name}"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Pros:**")
                pros = vehicle_rec.get('pros', [])
                for pro in pros:
                    st.markdown(f"• {pro}")
            
            with col2:
                st.markdown("**⚠️ Cons:**")
                cons = vehicle_rec.get('cons', [])
                for con in cons:
                    st.markdown(f"• {con}")
            
            # Best use case
            best_use_case = vehicle_rec.get('best_use_case', '')
            if best_use_case:
                st.markdown(f"**🎯 Best For:** {best_use_case}")
            
            # Overall recommendation
            overall_rec = vehicle_rec.get('overall_recommendation', '')
            if overall_rec:
                st.markdown(f"**💡 Recommendation:** {overall_rec}")

def export_comparison_report(comparison_results: Dict[str, Any], 
                           recommendations: Dict[str, Any]):
    """Export detailed comparison report"""
    
    st.subheader("📄 Export Report")
    
    vehicles = comparison_results.get('vehicles', [])
    if not vehicles:
        st.warning("No data available for export.")
        return
    
    # Generate report content
    report_content = f"""# Vehicle Comparison Report

## Executive Summary

**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
**Vehicles Compared:** {len(vehicles)}

"""
    
    # Best overall choice
    best_overall = comparison_results.get('best_overall')
    if best_overall:
        # Fix annual cost for report
        annual_cost = best_overall.get('annual_cost', 0)
        total_cost = best_overall.get('total_cost', 0)
        analysis_years = best_overall.get('analysis_years', 5)
        
        if analysis_years > 0 and annual_cost > total_cost * 0.8:
            annual_cost = total_cost / analysis_years
        
        report_content += f"""### 🏆 Best Overall Choice
**{best_overall['vehicle_name']}** ({best_overall['transaction_type']})
- Annual Cost: ${annual_cost:,.0f}
- Total Cost: ${total_cost:,.0f}
- Affordability: {'Good' if best_overall.get('is_affordable', False) else 'Marginal'}

"""
    
    # Detailed comparison
    report_content += "## Detailed Comparison\n\n"
    
    for i, vehicle in enumerate(vehicles, 1):
        # Fix annual cost for each vehicle in report
        annual_cost = vehicle.get('annual_cost', 0)
        total_cost = vehicle.get('total_cost', 0)
        analysis_years = vehicle.get('analysis_years', 5)
        
        if analysis_years > 0 and annual_cost > total_cost * 0.8:
            annual_cost = total_cost / analysis_years
        
        report_content += f"""### {i}. {vehicle['vehicle_name']}
- **Transaction Type:** {vehicle['transaction_type']}
- **Annual Cost:** ${annual_cost:,.0f}
- **Total Cost:** ${total_cost:,.0f}
- **Monthly Cost:** ${annual_cost/12:,.0f}
- **Cost per Mile:** ${vehicle.get('cost_per_mile', 0):.3f}
- **Affordable:** {'Yes' if vehicle.get('is_affordable', False) else 'No'}

"""
    
    # Key insights
    insights = recommendations.get('key_insights', [])
    if insights:
        report_content += "## Key Insights\n\n"
        for insight in insights:
            report_content += f"- {insight}\n"
    
    report_content += """

---
*Report generated by Vehicle TCO Calculator*
*This analysis is based on estimates and assumptions. Actual costs may vary.*
"""
    
    # Create download button
    st.download_button(
        label="📄 Download Comparison Report",
        data=report_content,
        file_name=f"Vehicle_Comparison_Report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )
    
    st.success("✅ Comparison report prepared for download!")