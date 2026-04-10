export default {
  carbon: {
    title: 'Carbon Tracking',
    loading: 'Loading...',
    error_loading: 'Failed to load data: {error}',
    all_productions: 'All Productions',

    units: {
      per_week: '{unit} / week',
      logged: 'logged'
    },

    stats: {
      total_project_emissions: 'Total Project Emissions',
      total_studio_emissions: 'Total Studio Emissions',
      weekly_average: 'Weekly Average Emissions',
      total_man_days: 'Total Man-Days',
      vs_last_week: 'vs last week',
      based_on_logged_time: 'Based on logged time',
      cumulative_all_steps: 'Cumulative across all steps',
      cumulative_all_productions: 'Cumulative across all productions'
    },

    tabs: {
      matrix_view: 'Matrix view',
      step_breakdown: 'Step breakdown',
      production_breakdown: 'Production breakdown'
    },

    filters: {
      shots: 'Shots',
      assets: 'Assets'
    },

    matrix: {
      all: 'ALL',
      all_steps: 'ALL STEPS',
      all_row: 'All {label}',
      productions: 'PRODUCTIONS',
      production: 'PRODUCTION',
      production_step: 'PRODUCTION STEP',
      emission_impact: 'EMISSION IMPACT',
      value: 'VALUE',
      asset_types: 'ASSET TYPES',
      episodes: 'EPISODES',
      sequences: 'SEQUENCES'
    },

    legend: {
      lowest: 'Lowest Impact',
      medium: 'Medium Impact',
      highest: 'Highest Impact'
    },

    info: {
      title: 'How is carbon calculated?',
      description:
        'Emissions are estimated based on logged working time per task and geographic carbon factors specific to each production facility.',
      work_time: 'Work Time',
      people: 'People',
      carbon_factor: 'Carbon Factor',
      factors_title: "WHAT'S INCLUDED IN THE CARBON FACTOR:",
      workstation: 'Workstation',
      building_energy: 'Building Energy',
      electricity_mix: 'Electricity Mix',
      meals: 'Meals',
      cloud_infra: 'Cloud & Infra',
      commute: 'Commute',
      read_doc: 'Read full documentation'
    },

    disclaimer:
      'Calculations are performed according to best practices in effect at the time the tool was released. However, the values provided by Kitsu remain estimates. Consulting kgCO₂e estimates in Kitsu does not exempt you from your regulatory obligations, nor does it replace the calculators, methods, or approved frameworks required by your partners or supervisory bodies (including the CNC).'
  }
}
