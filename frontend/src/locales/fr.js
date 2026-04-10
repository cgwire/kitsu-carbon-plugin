export default {
  carbon: {
    title: 'Bilan Carbone',
    loading: 'Chargement...',
    error_loading: 'Erreur lors du chargement : {error}',
    all_productions: 'Toutes les productions',

    units: {
      per_week: '{unit} / semaine',
      logged: 'comptabilisés'
    },

    stats: {
      total_project_emissions: 'Émissions totales du projet',
      total_studio_emissions: 'Émissions totales du studio',
      weekly_average: 'Moyenne hebdomadaire',
      total_man_days: 'Total homme-jours',
      vs_last_week: 'vs semaine précédente',
      based_on_logged_time: 'Basé sur le temps saisi',
      cumulative_all_steps: 'Cumulé sur toutes les étapes',
      cumulative_all_productions: 'Cumulé sur toutes les productions'
    },

    tabs: {
      matrix_view: 'Vue matrice',
      step_breakdown: 'Par étape',
      production_breakdown: 'Par production'
    },

    filters: {
      shots: 'Plans',
      assets: 'Assets'
    },

    matrix: {
      all: 'TOUT',
      all_steps: 'TOUTES LES ÉTAPES',
      all_row: 'Tous les {label}',
      productions: 'PRODUCTIONS',
      production: 'PRODUCTION',
      production_step: 'ÉTAPE DE PRODUCTION',
      emission_impact: "IMPACT D'ÉMISSION",
      value: 'VALEUR',
      asset_types: "TYPES D'ASSETS",
      episodes: 'ÉPISODES',
      sequences: 'SÉQUENCES'
    },

    legend: {
      lowest: 'Impact faible',
      medium: 'Impact moyen',
      highest: 'Impact élevé'
    },

    info: {
      title: 'Comment le carbone est-il calculé ?',
      description:
        'Les émissions sont estimées à partir du temps de travail saisi par tâche et des facteurs carbone géographiques propres à chaque site de production.',
      work_time: 'Temps de travail',
      people: 'Personnes',
      carbon_factor: 'Facteur carbone',
      factors_title: 'CE QUI EST INCLUS DANS LE FACTEUR CARBONE :',
      workstation: 'Poste de travail',
      building_energy: 'Énergie du bâtiment',
      electricity_mix: 'Mix électrique',
      meals: 'Repas',
      cloud_infra: 'Cloud & Infra',
      commute: 'Trajets domicile-travail',
      read_doc: 'Lire la documentation complète'
    },

    disclaimer:
      "Les calculs sont réalisés selon les meilleures pratiques en vigueur à la date de mise en ligne de l'outil. Néanmoins, les valeurs fournies par Kitsu demeurent des estimations. La consultation des estimations de kgCO₂e dans Kitsu ne saurait vous dispenser de vos obligations réglementaires ni se substituer aux calculateurs, méthodes ou référentiels homologués exigés par vos partenaires ou organismes de tutelle (notamment le CNC)."
  }
}
