from viktor import ViktorController
from viktor.result import OptimizationResult, OptimizationResultElement
from viktor.views import DataView, DataGroup, DataItem, DataResult, PlotlyView, PlotlyResult, WebView, WebResult
from viktor.parametrization import ViktorParametrization, Step, TextField, NumberField, OptionField, Table, \
    OptimizationButton

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import aashto93
import solvesection

from pathlib import Path

class Parametrization(ViktorParametrization):
    step_1 = Step("Step 1: Traffic Conditions", views=["show_traffic_results"])
    step_1.name = TextField("Road Name")
    step_1.adt = NumberField("Average Daily Traffic (ADT)", default=1000,
                             description="""
Typical ranges:
- Residential: < 2000
- Collector: 2000 - 12000
- Arterial: > 12000
""",
                             )
    step_1.distribution = NumberField("Directional Distribution (%)", default=50, description="Typically 50% unless there is a difference between inbound/outbound trips")
    step_1.lane_distribution = NumberField("Lane Distribution (%)", default=100, description="Typically 100% unless there are multiple lanes")
    step_1.trucks = NumberField("Percentage of Trucks (%)", default=5, description="Commercial truck traffic. Typically less than 5% except for highways and freeways")
    step_1.lef = NumberField("Load Equivalent Factor", default=1.0,
                             description="""
Typical Values:
- School Bus: 0.7
- Metro Bus: 1.6
- Delivery Truck: 0.8
- Tractor-Trailer: 1.2
"""
                             )
    step_1.service_years = NumberField("Service Life of Roads (yrs)", default=20, )
    step_1.serviceability = NumberField("Allowable Change in Serviceability Factor", default=2.5, description="Index ranges from 1.0 (poor) to 5.0 (excellent). Allowable deterioration before repair is typically 2.0-4.0.")
    step_1.growth_rate = NumberField("Growth Rate (%)", default=2, )
    step_1.typical_profile_height = NumberField("Typical Profile Height (in)", default=0, description="This is the difference (+/-) between the top of the road profile and the surface from which pavement construction starts (may be natural ground or bottom of removed material)")
    step_2 = Step("Step 2: Design Criteria", views=["show_design_results", "design_html"])
    step_2.reliability = NumberField("Reliability (%)", default=95, description="Probability of maintaining service level for the design life")
    step_2.standard_error = NumberField("Standard Error (%)", default=45,
                                        description="40-50 for asphalt, 35-40 for concrete")
    step_2.serviceability_change = NumberField("Serviceability Index Change", default=2.5,
                                               description="Index ranges from 1.0 (poor) to 5.0 (excellent). Allowable deterioration before repair is typically 2.0-4.0.")
    step_2.soil_resilient_modulus = NumberField("Soil Resilient Modulus", default=3000,
                                                description="""
Common Values:
- Clays: 5000
- Silts: 15000
- Sand: 25000
- Gravel: 35000""")
    step_3 = Step("Step 3: Materials", views=["material_html"])
    _material_table_defaults = [
        {"mat_name": "Asphalt Surface (1/2in)", "sn": 0.44, "min": 1.5, "max": 4.0, "density": 145.0, "cost": 130.0,
         "unit": "ton", "surface": "Yes", "subgrade": "No", "alkaline": "No"},
        {"mat_name": "Asphalt Binder (1in)", "sn": 0.44, "min": 3.0, "max": 6.0, "density": 140.0, "cost": 120.0,
         "unit": "ton", "surface": "No", "subgrade": "No", "alkaline": "No"},
        {"mat_name": "Crushed Rock Base (3/4in minus)", "sn": 0.13, "min": 2.0, "max": 8.0, "density": 135.0,
         "cost": 35.0,
         "unit": "ton", "surface": "No", "subgrade": "No", "alkaline": "No"},
        {"mat_name": "Stone Backfill (6in coarse aggregate)", "sn": 0.1, "min": 18.0, "max": 48.0, "density": 120.0,
         "cost": 45.0,
         "unit": "ton", "surface": "No", "subgrade": "No", "alkaline": "No"},
        {"mat_name": "Flowable Fill (Concrete", "sn": 0.2, "min": 4.0, "max": 60.0, "density": 130.0, "cost": 650.0,
         "unit": "cyd", "surface": "No", "subgrade": "No", "alkaline": "Yes"},
        {"mat_name": "Lime Treated Subgrade", "sn": 0.2, "min": 4.0, "max": 8.0, "density": 120.0, "cost": 300.0,
         "unit": "cyd", "surface": "No", "subgrade": "Yes", "alkaline": "Yes"},
        {"mat_name": "Concrete Base (8in PCC)", "sn": 0.5, "min": 8.0, "max": 8.0, "density": 150.0, "cost": 150.0,
         "unit": "sqyd", "surface": "No", "subgrade": "No", "alkaline": "Yes"},
    ]
    step_3.table = Table("Materials", default=_material_table_defaults)
    step_3.table.mat_name = TextField("Material Name")
    step_3.table.sn = NumberField("Structural Number")
    step_3.table.min = NumberField("Minimum Lift (in.)")
    step_3.table.max = NumberField("Maximum Lift (in.)")
    step_3.table.density = NumberField("Density (lb/ft^3)")
    step_3.table.cost = NumberField("Unit Cost ($/u)")
    step_3.table.unit = OptionField("Unit", options=["ton", "cyd", "sqyd"])
    step_3.table.surface = OptionField("Surface", options=["Yes", "No"])
    step_3.table.subgrade = OptionField("Subgrade Treatment", options=["Yes", "No"])
    step_3.table.alkaline = OptionField("Alkaline", options=["Yes", "No"])
    step_3.excavation_cost = NumberField("Excavation Cost ($/cyd)", default=20.0)
    step_3.embankment_cost = NumberField("Embankment Cost ($/cyd)", default=10.0)
    step_4 = Step("Step 4: Solve", views=["optimize", "optimize_graph", "optimize_html"])
    step_4.goal_sn = NumberField("Required Structural Number", default=5.0,
                                 description="Use the value from Step 2 or provide an alternative.")


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @DataView("Traffic Results", duration_guess=1)
    def show_traffic_results(self, params, **kwargs):
        trips = aashto93.total_trips(params.step_1.adt, params.step_1.service_years, params.step_1.growth_rate / 100)
        esals = aashto93.trips_to_esals(trips * params.step_1.trucks / 100, params.step_1.distribution / 100,
                                        params.step_1.lane_distribution / 100, params.step_1.lef)
        data = DataGroup(
            DataItem("Total Trips", round(trips, -2)),
            DataItem("ESAL", round(esals, -1)),
        )
        return DataResult(data)

    @DataView("Design Results", duration_guess=1)
    def show_design_results(self, params, **kwargs):
        ## Values are stateless, so we recaulculate ##
        trips = aashto93.total_trips(params.step_1.adt, params.step_1.service_years, params.step_1.growth_rate / 100)
        esals = aashto93.trips_to_esals(trips * params.step_1.trucks / 100, params.step_1.distribution / 100,
                                        params.step_1.lane_distribution / 100, params.step_1.lef)
        ## end copy ##
        z = params.step_2.reliability / 100
        so = params.step_2.standard_error / 100
        psi = params.step_2.serviceability_change
        mr = params.step_2.soil_resilient_modulus
        sn = aashto93.solve_sn(z, so, psi, mr, esals)
        data = DataGroup(
            DataItem("Structural Number", round(sn, 2)),
        )
        return DataResult(data)

    @DataView("Optimization Results", duration_guess=5)
    def optimize(self, params, **kwargs):
        materials = params.step_3.table
        goal_sn = params.step_4.goal_sn
        combined_data = []
        profile = params.step_1.typical_profile_height
        excavation = params.step_3.excavation_cost
        embankment = params.step_3.embankment_cost
        top_3 = solvesection.solve(materials, goal_sn, profile, embankment, excavation)[:3]
        for section in top_3:
            section_data = []
            structural_number = round(solvesection.section_sn(section), 2)
            for layer in section:
                name = layer.name
                thickness = layer.thickness
                section_data.append(DataItem(name, thickness))
            combined_data.append((structural_number, section_data))
        raw_costs = [solvesection.section_cost(section, profile, embankment, excavation) for section in top_3]
        formatted_costs = [f'${cost:.2f}/SY' for cost in raw_costs]
        group_a = DataItem('Section A', combined_data[0][0], prefix="SN", subgroup=DataGroup(*combined_data[0][1]))
        group_b = DataItem('Section B', combined_data[1][0], prefix="SN", subgroup=DataGroup(*combined_data[1][1]))
        group_c = DataItem('Section C', combined_data[2][0], prefix="SN", subgroup=DataGroup(*combined_data[2][1]))
        cost_a = DataItem('Section A Cost', formatted_costs[0])
        cost_b = DataItem('Section B Cost', formatted_costs[1])
        cost_c = DataItem('Section C Cost', formatted_costs[2])
        return DataResult(DataGroup(group_a, group_b, group_c, cost_a, cost_b, cost_c))

    @PlotlyView("Optimization Graph", duration_guess=5)
    def optimize_graph(self, params, **kwargs):
        # There is a lot of duplication here. TODO: More narrow functions in solvesection module
        materials = params.step_3.table
        goal_sn = params.step_4.goal_sn
        profile = params.step_1.typical_profile_height
        embankment = params.step_3.embankment_cost
        excavation = params.step_3.excavation_cost
        # Get trial sections
        material_list = solvesection.make_material_list(materials)
        sample_population = 5000
        trial_sections = [solvesection.make_trial_section(material_list) for _ in range(sample_population)]
        trial_xs = [solvesection.section_sn(section) for section in trial_sections]
        trial_ys = [solvesection.section_cost(section, profile, embankment, excavation) for section in trial_sections]
        solved_sections = solvesection.solve(materials, goal_sn, profile, embankment, excavation)
        solved_xs = [solvesection.section_sn(section) for section in solved_sections]
        solved_ys = [solvesection.section_cost(section, profile, embankment, excavation) for section in solved_sections]
        fig = make_subplots(rows=2, cols=1, subplot_titles=(f"Initial Sections (n={sample_population})", f"Optimized Sections (n={len(solved_sections)})"))
        fig.add_trace(go.Scatter(x=trial_xs, y=trial_ys, mode="markers", name="Initial Sections"), row=1, col=1)
        fig.add_trace(go.Scatter(x=solved_xs, y=solved_ys, mode="markers", name="Optimized Sections"), row=2, col=1)
        fig.update_yaxes(title_text="Cost ($/sy)", row=2, col=1)
        fig.update_yaxes(title_text="Cost ($/sy)", row=1, col=1)
        fig.update_xaxes(title_text="Structural Number", row=1, col=1)
        fig.update_xaxes(title_text="Structural Number", row=2, col=1)
        fig.update_layout(title="Optimization Graph")
        return PlotlyResult(fig.to_json())

    # Explainers
    @WebView("Design Explanation", duration_guess=1)
    def design_html(self, params, **kwargs):
        content = Path(__file__).parent / "docs" / "html" / "Design_Explainer.html"
        return WebResult.from_path(content)

    @WebView("Material Explanation", duration_guess=1)
    def material_html(self, params, **kwargs):
        content = Path(__file__).parent / "docs" / "html" / "Materials_Explainer.html"
        return WebResult.from_path(content)

    @WebView("Optimize Explanation", duration_guess=1)
    def optimize_html(self, params, **kwargs):
        content = Path(__file__).parent / "docs" / "html" / "Optimize_Explainer.html"
        return WebResult.from_path(content)
