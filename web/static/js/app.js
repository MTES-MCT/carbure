const dt_config = {}
const lot_errors = {}
const selected_rows = []

const table_columns_drafts_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.biocarburant.name }},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.matiere_premiere.name }},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.pays_origine.code_pays }},

{title:'EEC', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', shown: false, hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', shown: false, hidden: true, can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°Document douanier', can_hide: true, can_duplicate: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.dae}},
{title:'Champ libre', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, tooltip: 'Champ libre - Référence client', render: (data, type, full, meta) => {return full.tx.fields.champ_libre}},
{title:'Date de livraison', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_date}},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]

const table_columns_corrections_v2 = [
{title:'Période', can_hide: true, data:'period'},
{title:'Numéro de lot', can_hide: true, data:'carbure_id'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.biocarburant.name }},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.matiere_premiere.name }},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.pays_origine.code_pays }},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},
{title:'N°Document douanier', can_hide: true, can_duplicate: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.dae}},
{title:'Champ libre', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, tooltip: 'Champ libre - Référence client', render: (data, type, full, meta) => {return full.tx.fields.champ_libre}},
{title:'Date de livraison', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_date}},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]


const table_columns_received_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Fournisseur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.tx.fields.vendor_is_in_carbure ? full.tx.fields.carbure_vendor : `<i>${full.tx.fields.unknown_vendor}</i>` }},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.biocarburant.name }},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.matiere_premiere.name }},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.pays_origine.code_pays }},

{title:'EEC', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', hidden: true, can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.dae}},
{title:'Référence', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, tooltip: 'Champ libre - Référence client', render: (data, type, full, meta) => {return full.tx.fields.champ_libre}},
{title:'Date d\'entrée<br /> en EA', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_date}},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]

const table_columns_valid_v2 = [
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Fournisseur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.tx.fields.vendor_is_in_carbure ? full.tx.fields.carbure_vendor : `<i>${full.tx.fields.unknown_vendor}</i>` }},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.biocarburant.name }},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.matiere_premiere.name }},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.pays_origine.code_pays }},

{title:'EEC', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', hidden: true, can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', hidden: true, can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.dae}},
{title:'Référence', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, tooltip: 'Champ libre - Référence client', render: (data, type, full, meta) => {return full.tx.fields.champ_libre}},
{title:'Date d\'entrée<br /> en EA', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_date}},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]


var table_columns_operators_affiliated = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Période', can_hide: true, can_export: true, data:'period'},
{title:'Fournisseur', can_hide: true,  can_export: true, data:'producer_name'},
{title:'Site de<br />Production', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Numéro de lot', can_hide: true, can_duplicate: false, can_export: true, data:'carbure_id'},
{title:'Volume<br /> à 20°C<br />en Litres', can_hide: true,  can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true,  can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true,  can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true,  can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true,  can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true,  can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true,  can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true,  can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true,  can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true,  can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br />en EA', can_hide: true,  can_export: true, data:'ea_delivery_date'},
{title:'Site de livraison', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
{title:'Statut', can_hide: true, can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_status'},
]

var table_columns_operators_declared = [
{title:'Période', can_hide: true, can_export: true, data:'period'},
{title:'Numéro de lot', can_hide: true, can_duplicate: false, can_export: true, data:'carbure_id'},
{title:'Fournisseur', can_hide: true,  can_export: true, data:'producer_name'},
{title:'Site de<br />Production', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Volume<br /> à 20°C<br />en Litres', can_hide: true,  can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true,  can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true,  can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true,  can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true,  can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true,  can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true,  can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true,  can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true,  can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true,  can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br />en EA', can_hide: true,  can_export: true, data:'ea_delivery_date'},
{title:'Site de livraison', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
]


var table_columns_administrators = [
{title:'Producteur', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'producer_name'},
{title:'Site de<br />Production', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Numéro de lot', can_hide: true, can_duplicate: false, can_export: true, data:'carbure_id'},
{title:'Volume<br /> à 20°C<br />en Litres', can_hide: true,  can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true,  can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true,  can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true,  can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true,  can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true,  can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true,  can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true,  can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true,  can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true,  can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true,  is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true,  can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br />en EA', can_hide: true,  can_export: true, data:'ea_delivery_date'},
{title:'Client', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'ea_name'},
{title:'Site de livraison', can_hide: true,  can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
]

/* modals management */
var modals = document.getElementsByClassName("modal__backdrop");

for (let i = 0, len = modals.length; i < len; i++) {
  let modalid = modals[i].id
  let modal = document.getElementById(modalid)
  let btn_open_id = "btn_open_" + modalid
  let btn_close_id = "btn_close_" + modalid
  var btn_open_modal = document.getElementById(btn_open_id)
  var btn_close_modal = document.getElementById(btn_close_id)

  if (btn_open_modal !== null) {
    btn_open_modal.onclick = function() {
      modal.style.display = "flex"
    }
  }

  if (btn_close_modal !== null) {
    btn_close_modal.onclick = function() {
      modal.style.display = "none"
    }
  }
}
// clicking outside of the modal window will close it
window.onclick = function(event) {
  for (let i = 0, len = modals.length; i < len; i++) {
    let modalid = modals[i].id
    let modal = document.getElementById(modalid)
    if (event.target == modal) {
      modal.style.display = "none"
    }
  }
}

// escape key
document.addEventListener('keydown', function(event) {
  if (event.keyCode === 27) {
    for (let i = 0, len = modals.length; i < len; i++) {
      let modalid = modals[i].id
      let modal = document.getElementById(modalid)
      modal.style.display = "none"
    }
  }
})

/* Producers */
/* Producers - settings */
var btns_edit_site = document.getElementsByClassName("btn_open_modal_site_edit")
for (let i = 0, len = btns_edit_site.length; i < len; i++) {
  let btn = btns_edit_site[i]
  let site_id = btn.dataset.siteid
  btn.onclick = function() {
    let modal = document.getElementById("modal_site_edit")
    modal.style.display = "flex"
    $("#modal_site_edit_site").val(site_id)
  }
}

var btns_delete_certif = document.getElementsByClassName("btn_open_modal_delete_certif")
for (let i = 0, len = btns_delete_certif.length; i < len; i++) {
  let btn = btns_delete_certif[i]
  let crtid = btn.dataset.crtid
  btn.onclick = function() {
    let modal = document.getElementById("modal_certif_delete")
    modal.style.display = "flex"
    $("#modal_certif_crtid").val(crtid)
    $("#modal_certif_delete_site").text(btn.dataset.site)
    $("#modal_certif_delete_num").text(btn.dataset.num)
    $("#modal_certif_delete_expi").text(btn.dataset.expi)
  }
}

var btns_delete_right = document.getElementsByClassName("btn_open_modal_right_delete")
for (let i = 0, len = btns_delete_right.length; i < len; i++) {
  let btn = btns_delete_right[i]
  btn.onclick = function() {
    let modal = document.getElementById("modal_right_delete")
    modal.style.display = "flex"
    $("#modal_right_delete_id").val(btn.dataset.rightid)
    $("#modal_right_delete_user").text(btn.dataset.user)
    $("#modal_right_delete_entity").text(btn.dataset.entity)
  }
}


$("form").submit(function(event) {
  let form = $(this);
  let form_id = form.attr('id')
  let form_url = form.attr('data-url')
  let auto_reload = form.attr('data-reload')
  let err_msg_dom = $(`#${form_id}_err_message`)
  let success_msg_dom = $(`#${form_id}_success_message`)
  err_msg_dom.text("Envoi en cours, veuillez patienter...")
  var formdata = false;
  if (window.FormData){
    formdata = new FormData(form[0])
  }
  $.ajax({
    url         : form_url,
    data        : formdata ? formdata : form.serialize(),
    cache       : false,
    contentType : false,
    processData : false,
    type        : 'POST',
    success     : function(data, textStatus, jqXHR) {
      // Callback code
      err_msg_dom.text("")
      if (auto_reload === "0") {
      	  success_msg_dom.html(data.message)
      } else {
	      window.location.reload()
      }
    },
    error       : function(e) {
      if (e.status === 400) {
      	if (Array.isArray(e.responseJSON.results)) {
      		let text = ""
      		for (let i = 0, len = e.responseJSON.results.length; i < len; i++) {
      			text += `Lot ${e.responseJSON.results[i].lot_id}: ${e.responseJSON.results[i].message}<br />`
      		}
	   	    err_msg_dom.html(text)
      	  	success_msg_dom.html("")
      	} else {
    	    err_msg_dom.text(e.responseJSON.message)
      	  	success_msg_dom.html("")
	   	    console.log(`error ${JSON.stringify(e.responseJSON.extra)}`)
      	}
      } else {
        err_msg_dom.text("Server error. Please contact an administrator")
      	success_msg_dom.html("")
        console.log(`server error ${JSON.stringify(e)}`)
      }
    }
  });
  event.preventDefault()
})

$("#pagelength").on('change', function() {
  let pagelength = $("#pagelength").val()
  window.table.page.len(pagelength).draw()
})

$("#pagelength_valid").on('change', function() {
  let pagelength = $("#pagelength_valid").val()
  table_valid.page.len(pagelength).draw()
})

$("#pagelength_lots_admin").on('change', function() {
  let pagelength = $("#pagelength_lots_admin").val()
  table.page.len(pagelength).draw()
})


function loadTableSettings(table_columns, table_name) {
  var tableSettings = localStorage.getItem(table_name);
  if (tableSettings === undefined || tableSettings === null) {
    let nb_columns = table_columns.length
    columns = Array(nb_columns).fill(1);
    saveTableSettings(columns, table_name)
  } else {
    columns = JSON.parse(tableSettings)
    let nb_columns = table_columns.length
    if (columns.length !== nb_columns) {
      columns = Array(nb_columns).fill(1);
      saveTableSettings(columns, table_name)
    }
  }
  return columns
}

function loadAddLotSettings() {
  var addLotSettings = localStorage.getItem('addLotSettings');
  if (addLotSettings === undefined || addLotSettings === null) {
    let nb_columns = table.columns().data().length
    columns = Array(nb_columns).fill(1);
    saveAddLotSettings(columns)
  } else {
    columns = JSON.parse(addLotSettings)
  }
  return columns
}

function saveTableSettings(settings, table_name) {
  localStorage.setItem(table_name, JSON.stringify(settings));
}

function saveAddLotSettings(settings) {
  localStorage.setItem("addLotSettings", JSON.stringify(settings));
}

function showHideTableColumns(table, columns, dom) {
  /* display table columns depending on config */
  console.log(`showHideTableColumns for table ${columns} ${dom}`)
  let nb_columns = table.columns().data().length
  for (let i = 0, len = nb_columns; i < len; i++) {
    let isChecked = columns[i]
    let boxid = `#checkbox_${dom}${i}`
    var column = table.column(i)
    if (isChecked) {
      $(boxid).prop("checked", true);
      if (!column.visible()) {
        column.visible(!column.visible())
      }
    } else {
      $(boxid).prop("checked", false);
      if (column.visible()) {
        column.visible(!column.visible())
      }
    }
  }
}

function preCheckAddLotSettings(columns) {
  /* checks checkboxes according to config */
  let nb_columns = table_drafts.columns().data().length
  for (let i = 0, len = nb_columns; i < len; i++) {
    let isChecked = columns[i]
    let boxid = '#add_checkbox' + i
    if (isChecked) {
      $(boxid).prop("checked", true);
    } else {
      $(boxid).prop("checked", false);
    }
  }
}


function duplicate_lot(lot_id) {
  // get columns to duplicate
  var addLotSettings = loadAddLotSettings()
  var fields_to_ignore = []
  for (let i = 0, len = addLotSettings.length; i < len; i++) {
    if (addLotSettings[i] == 1) {
      continue
    }
    let field_name = table_columns_drafts[i].data
    fields_to_ignore.push(field_name)
  }
  let url = $("#duplicate_url").attr('data-url')
  $.ajax({
    url         : url,
    data        : {'lot_id': lot_id, 'fields':fields_to_ignore, 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
    type        : 'POST',
    success     : function(data, textStatus, jqXHR){
      // Callback code
      window.table_drafts.ajax.reload()
      selected_rows.pop()
      manage_actions()
    },
    error       : function(e) {
      if (e.status === 400) {
        alert(e.responseJSON.message)
        console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
      } else {
        alert("Server error. Please contact an administrator")
        console.log(`server error ${JSON.stringify(e)}`)
      }
    }
  })
}

function manage_validate_button() {
  // check if we have drafts
  let draft_present = false
  for (let i = 0, len = selected_rows.length; i < len; i++) {
    let rowdata = window.table.row(selected_rows[i]).data()
    let statut = rowdata.fields.status
    if (statut.toLowerCase() === "draft") {
      draft_present = true
      break;
    }
  }

  if (draft_present === true) {
    $("#btn_open_modal_validate_lots").addClass('primary')
    $("#btn_open_modal_validate_lots").css("pointer-events", "auto")
    $("#btn_open_modal_validate_lots").removeClass('secondary')
    // add drafts to validate modal
    $("#modal_validate_lots_list").empty()
    let to_validate = []
    for (let i = 0, len = selected_rows.length; i < len; i++) {
      let rowdata = window.table.row(selected_rows[i]).data()
      let statut = rowdata.fields.status
      if (statut.toLowerCase() === "draft") {
        $("#modal_validate_lots_list").append(`<li>${rowdata.fields.producer_is_in_carbure ? rowdata.fields.carbure_producer : rowdata.fields.unknown_producer} - ${rowdata.fields.volume} - ${rowdata.fields.biocarburant.name} - ${rowdata.fields.matiere_premiere.name}</li>`)
        to_validate.push(rowdata.pk)
      }
      $("#modal_validate_lots_lots").val(to_validate.join(","))
    }

  } else {
    $("#btn_open_modal_validate_lots").addClass('secondary')
    $("#btn_open_modal_validate_lots").css("pointer-events", "none")
    $("#btn_open_modal_validate_lots").removeClass('primary')
    // cleanup validate modal
    $("#modal_validate_lots_list").empty()
  }
}

function manage_delete_button() {
  let only_drafts_present = true
  for (let i = 0, len = selected_rows.length; i < len; i++) {
    let rowdata = window.table.row(selected_rows[i]).data()
    let statut = rowdata.fields.status
    if (statut.toLowerCase() !== "draft") {
      only_drafts_present = false
      break;
    }
  }
  let keys = Object.keys(selected_rows)
  if (keys.length > 0 && only_drafts_present === true) {
    $("#btn_open_modal_delete_lots").addClass('primary')
    $("#btn_open_modal_delete_lots").css("pointer-events", "auto")
    $("#btn_open_modal_delete_lots").removeClass('secondary')
    $("#modal_delete_lots_list").empty()
    let to_delete = []
    for (let i = 0, len = selected_rows.length; i < len; i++) {
      let rowdata = window.table.row(selected_rows[i]).data()
      let statut = rowdata.fields.status
      if (statut.toLowerCase() === "draft") {
        $("#modal_delete_lots_list").append(`<li>${rowdata.fields.producer_is_in_carbure ? rowdata.fields.carbure_producer : rowdata.fields.unknown_producer} - ${rowdata.fields.volume} - ${rowdata.fields.biocarburant.name} - ${rowdata.fields.matiere_premiere.name}</li>`)
        to_delete.push(rowdata.pk)
      }
      $("#modal_delete_lots_lots").val(to_delete.join(","))
    }
  } else {
    $("#btn_open_modal_delete_lots").addClass('secondary')
    $("#btn_open_modal_delete_lots").removeClass('primary')
    $("#btn_open_modal_delete_lots").css("pointer-events", "none")
    $("#modal_delete_lots_list").empty()
  }
}

function manage_duplicate_button() {
  if (selected_rows.length === 1) {
    let lot_id = window.table.row(selected_rows[0]).data().pk
    $("#duplicate_lot").attr("onclick", `duplicate_lot(${lot_id})`)
    $("#duplicate_lot").addClass('primary')
    $("#duplicate_lot").css("pointer-events", "auto")
    $("#duplicate_lot").removeClass('secondary')
  } else {
  	$("#duplicate_lot").addClass('secondary')
    $("#duplicate_lot").css("pointer-events", "none")
    $("#duplicate_lot").removeClass('primary')
  }
}

function check_production_sites() {
  $.ajax({
    url         : window.producers_api_production_sites_autocomplete + `?producer_id=${window.producer_id}&query=`,
    type        : 'GET',
    success     : function(data, textStatus, jqXHR) {
      if (data['suggestions'].length == 0) {
        $("#err_msg_dom").html('Aucun site de production enregistré')
      }
    },
    error       : function(e) {
      console.log(`error fetching existing production sites`)
    }
  })
}

function check_mps() {
  $.ajax({
    url         : window.producers_api_mps_autocomplete + `?producer_id=${window.producer_id}&query=`,
    type        : 'GET',
    success     : function(data, textStatus, jqXHR) {
      if (data['suggestions'].length == 0) {
        $("#err_msg_dom").html('Aucune matière première enregistrée dans votre profil')
      }
    },
    error       : function(e) {
      console.log(`error fetching mps`)
    }
  })
}

function check_biocarburants() {
  $.ajax({
    url         : window.producers_api_biocarburants_autocomplete + `?producer_id=${window.producer_id}&query=`,
    type        : 'GET',
    success     : function(data, textStatus, jqXHR) {
      if (data['suggestions'].length == 0) {
        $("#err_msg_dom").html('Aucun biocarburant enregistré dans votre profil')
      }
    },
    error       : function(e) {
      console.log(`error fetching biocarburants`)
    }
  })
}

function manage_actions() {
  // buttons Valider, Supprimer et Ajouter
  manage_validate_button()
  manage_delete_button()
  manage_duplicate_button()
}

function manage_actions_operators_affiliation() {
  // bouton Accepter Lots
  $("#modal_accept_lots_list").empty()
  if (selected_rows.length > 0) {
    $("#btn_open_modal_accept_lots").addClass('primary')
    $("#btn_open_modal_accept_lots").css("pointer-events", "auto")
    $("#btn_open_modal_accept_lots").removeClass('secondary')

		let to_accept = []
    for (let i = 0, len = selected_rows.length; i < len; i++) {
      let rowdata = table_operators_affiliations.row(selected_rows[i]).data()
      $("#modal_accept_lots_list").append(`<li>${rowdata['producer_name']} - ${rowdata['volume']} - ${rowdata['biocarburant_name']} - ${rowdata['matiere_premiere_name']}</li>`)
      to_accept.push(rowdata['lot_id'])
      $("#modal_accept_lots_lots").val(to_accept.join(","))
    }
  } else {
    $("#btn_open_modal_accept_lots").addClass('secondary')
    $("#btn_open_modal_accept_lots").css("pointer-events", "none")
    $("#btn_open_modal_accept_lots").removeClass('primary')
    // cleanup validate modal
    $("#modal_accept_lots_list").empty()
  }

}


function initDuplicateParams(table) {
  var list_columns_filter = $("#list_columns_filter")
  var list_columns_filter_html = ""
  for (let i = 0, len = table.length; i < len; i++) {
    let column = table[i]
    if (column.can_duplicate === true) {
      list_columns_filter_html += `<li class="flex-item-a"><input type="checkbox" id="add_checkbox${i}" class="toggle-lot-param" data-column="${i}"><label for="add_checkbox${i}" class="label-inline">${column.title}</label></li>`
    }
  }
  list_columns_filter.append(list_columns_filter_html)
}

function initFilters(table, dom) {
  console.log(`initializing filters for table ${dom}`)
  var table_columns_filter = $(`#table_columns_${dom}_filter`)
  var table_columns_filter2 = $(`#table_columns_${dom}_filter2`)
  var columns_filter_html = ""
  var columns_filter_html2 = ""
  for (let i = 0, len = table.length; i < len; i++) {
    let column = table[i]
    if (column.can_hide === true) {
      // use two columns
      if (i <= (len / 2)) {
        columns_filter_html += `<tr><td><input type="checkbox" id="checkbox_${dom}${i}" class="toggle-vis" data-column="${i}" data-table="${dom}"></td><td><label for="checkbox${i}" class="label-inline">${column.title}</label></td></tr>`
      } else {
        columns_filter_html2 += `<tr><td><input type="checkbox" id="checkbox_${dom}${i}" class="toggle-vis" data-column="${i}" data-table="${dom}"></td><td><label for="checkbox${i}" class="label-inline">${column.title}</label></td></tr>`
      }
    }
  }
  table_columns_filter.append(columns_filter_html)
  table_columns_filter2.append(columns_filter_html2)
}

function updateDataTableSelectAllCtrl(table){
   var $table             = table.table().node();
   var $chkbox_all        = $('tbody input[type="checkbox"]', $table);
   var $chkbox_checked    = $('tbody input[type="checkbox"]:checked', $table);
   var chkbox_select_all  = $('thead input[name="select_all"]', $table).get(0);

   // If none of the checkboxes are checked
   if($chkbox_checked.length === 0){
      chkbox_select_all.checked = false;
      if('indeterminate' in chkbox_select_all){
         chkbox_select_all.indeterminate = false;
      }

   // If all of the checkboxes are checked
   } else if ($chkbox_checked.length === $chkbox_all.length){
      chkbox_select_all.checked = true;
      if('indeterminate' in chkbox_select_all){
         chkbox_select_all.indeterminate = false;
      }

   // If some of the checkboxes are checked
   } else {
      chkbox_select_all.checked = true;
      if('indeterminate' in chkbox_select_all){
         chkbox_select_all.indeterminate = true;
      }
   }
}

function init_datatables_drafts(url) {
  // tab Drafts
  if (!$.fn.DataTable.isDataTable('#datatable_drafts')) {
      // create empty footer
    let empty_footer = `<tr>${Array(table_columns_drafts.length).fill("<th></th>").join('')}</tr>`
    $("#datatable_drafts tfoot").append(empty_footer)

    var table_drafts = $('#datatable_drafts').DataTable({
      paging: true,
      info: true,
      scrollX: true,
      scrollY: 1000,
      scrollCollapse: true,
      language: {
          search: "Rechercher:",
          paginate: {
              first:    '«',
              previous: '‹',
              next:     '›',
              last:     '»'
          },
          aria: {
              paginate: {
                  first:    'Première',
                  previous: 'Précédente',
                  next:     'Suivante',
                  last:     'Dernière'
              }
          }
      },
      dom: 'rtp',
      columnDefs: [
        {
          className: "dt-center",
          targets: "_all",
          render: function(data, type, row, meta) {
            let col_name = table_columns_drafts[meta.col].data
            let lot_id = row['lot_id']
            if (lot_id in lot_errors) {
              if (col_name in lot_errors[lot_id]) {
                let error = lot_errors[lot_id][col_name]
                return `<span style="color:tomato;">${error}</span>`
              }
            }
            return data
          }
        },
        {
          targets: 0,
          searchable:false,
          orderable:false,
          width:'1%',
          className: 'dt-body-center',
          render: function (data, type, full, meta) {
             return '<input type="checkbox">';
          }
        }
      ],
      order: [[ 1, 'desc' ]],
      columns: table_columns_drafts,
      ajax: {
        url: url,
        dataSrc: function(res) {
          lots = res['lots']
          for (let i = 0, len = lots.length; i < len; i++) {
            // add checkbox on the fly
            lots[i]["checkbox"] = `<input type="checkbox" />`
          }
          errors = res['errors']
          for (let i = 0, len = errors.length; i < len; i++) {
            let error = errors[i]
            let lot_id = error.lot_id
            if (!(lot_id in lot_errors)) {
              lot_errors[lot_id] = {}
            }
            lot_errors[lot_id][error.field] = error.value
          }
          return lots
        }
      },
      initComplete: function () {
        count = 0;
        this.api().columns().every(function () {
          var column = this;
          let table_column = table_columns_drafts[column.index()]
          if (table_column.can_filter === true) {
            var select = $('<select id="select_' + table_column.data + '" class="select2" ></select>')
                .appendTo($(column.footer()).empty())
                .on('change', function () {
                  //Get the "text" property from each selected data
                  //regex escape the value and store in array
                  var data = $.map($(this).select2('data'), function(value, key) {
                    return value.text ? '^' + $.fn.dataTable.util.escapeRegex(value.text) + '$' : null
                  })
                  //if no data selected use ""
                  if (data.length === 0) {
                    data = [""]
                  }
                  //join array into string with regex or (|)
                  var val = data.join('|')
                  //search for the option(s) selected
                  column.search(val ? val : '', true, false).draw()
                })
            column.data().unique().sort().each(function (d, j) {
              if (d === "") {
                return
              }
              select.append('<option value="'+d+'">'+d+'</option>');
            })
            //use column title as selector and placeholder
            $('#select_' + table_column.data).select2({
              multiple: true,
              closeOnSelect: true,
              placeholder: "Filtrer " + (table_column.filter_title  ? table_column.filter_title : table_column.title),
              placeholderOption: function () { return undefined; }
            });
            //initially clear select otherwise first option is selected
            $('.select2').val(null).trigger('change')
          } else {
            $(column.footer()).append()
          }
        }).draw()
      }
    })

    $("#datatable_drafts tbody").on('click', 'td',  (e) => {
      display_producers_lot_modal(table_drafts, table_columns_drafts, e)
    })
    window.table_drafts = table_drafts
    $('#input_search_datatable').on('keyup', function() {
        table_drafts.search(this.value).draw();
    })

    // Handle click on checkbox
    $('#datatable_drafts tbody').on('click', 'input[type="checkbox"]', function(e) {
      var $row = $(this).closest('tr');
      // Get row data
      var rowId = table_drafts.row($row).index();
      // Determine whether row ID is in the list of selected row IDs
      var index = $.inArray(rowId, selected_rows);
      // If checkbox is checked and row ID is not in list of selected row IDs
      if(this.checked && index === -1) {
        selected_rows.push(rowId);
      // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
      } else if (!this.checked && index !== -1) {
        selected_rows.splice(index, 1);
      }
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table_drafts);
      // Prevent click event from propagating to parent
      e.stopPropagation();
      // Show/Hide buttons depending on selected_rows content
      manage_actions()
    })


    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table_drafts.table().container()).on('click', function(e){
      if(this.checked){
         $('#datatable_drafts tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_drafts tbody input[type="checkbox"]:checked').trigger('click');
      }
      // Prevent click event from propagating to parent
      e.stopPropagation();
    });

    // Handle table draw event
    table_drafts.on('draw', function(){
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table_drafts);
    });

    var producerDraftsTableSettings = loadTableSettings(table_columns_drafts, 'producerDraftsTableSettings')
    showHideTableColumns(table_drafts, producerDraftsTableSettings, 'drafts')
  } else {
    window.table_drafts.draw()
  }
}

function init_datatables_corrections(url) {
  if (!$.fn.DataTable.isDataTable('#datatable_corrections')) {
    var table_corrections = $("#datatable_corrections").DataTable({
      paging: false,
      info: false,
      scrollX: true,
      scrollY: 1000,
      scrollCollapse: true,
      dom: 't',
      fixedColumns: {
        leftColumns: 0,
        rightColumns: 1,
      },
      columns: table_columns_producers_corrections,
      ajax: {
        url: url,
        dataSrc: function(data) {
          return data.lots
        },
      },
      initComplete: function () {
        count = 0;
        this.api().columns().every(function () {
          var column = this;
          let table_column = table_columns_producers_corrections[column.index()]
          if (table_column.can_filter === true) {
            var select = $('<select id="select_' + table_column.data + '_correction" class="select2" ></select>')
                .appendTo($(column.footer()).empty())
                .on('change', function () {
                  //Get the "text" property from each selected data
                  //regex escape the value and store in array
                  var data = $.map($(this).select2('data'), function(value, key) {
                    return value.text ? '^' + $.fn.dataTable.util.escapeRegex(value.text) + '$' : null
                  })
                  //if no data selected use ""
                  if (data.length === 0) {
                    data = [""]
                  }
                  //join array into string with regex or (|)
                  var val = data.join('|')
                  //search for the option(s) selected
                  column.search(val ? val : '', true, false).draw()
                })
            column.data().unique().sort().each(function (d, j) {
              if (d === "") {
                return
              }
              select.append('<option value="'+d+'">'+d+'</option>');
            })
            //use column title as selector and placeholder
            $('#select_' + table_column.data + '_correction').select2({
              multiple: true,
              closeOnSelect: true,
              placeholder: "Filtrer " + (table_column.filter_title  ? table_column.filter_title : table_column.title),
              placeholderOption: function () { return undefined; }
            });
            //initially clear select otherwise first option is selected
            $('.select2').val(null).trigger('change')
          } else {
            $(column.footer()).append()
          }
        }).draw()
      }
    })
    $("#datatable_corrections tbody").on('click', 'td',  (e) => {
      display_producers_lot_modal(table_corrections, table_columns_producers_corrections, e)
    })
    window.table_corrections = table_corrections
    var producerErrorsTableSettings = loadTableSettings(table_columns_producers_corrections, 'producerErrorsTableSettings')
    showHideTableColumns(table_corrections, producerErrorsTableSettings, 'errors')
  } else {
    window.table_corrections.draw()
  }
}

function init_datatables_validated(url) {
  if (!$.fn.DataTable.isDataTable('#datatable_valid')) {
    let empty_footer = `<tr>${Array(table_columns_producers_validated.length).fill("<th></th>").join('')}</tr>`
    $("#datatable_valid tfoot").append(empty_footer)

    var table_valid = $("#datatable_valid").DataTable({
      paging: false,
      info: false,
      scrollX: true,
      scrollY: 1000,
      scrollCollapse: true,
      dom: 't',
      fixedColumns: {
        leftColumns: 0,
        rightColumns: 1,
      },
      columns: table_columns_producers_validated,
      ajax: {
        url: url,
        dataSrc: function(data) {
          return data.lots
        },
      },
      initComplete: function () {
        count = 0;
        this.api().columns().every(function () {
          var column = this;
          let table_column = table_columns_producers_validated[column.index()]
          if (table_column.can_filter === true) {
            var select = $('<select id="select_' + table_column.data + '_valid" class="select2" ></select>')
                .appendTo($(column.footer()).empty())
                .on('change', function () {
                  //Get the "text" property from each selected data
                  //regex escape the value and store in array
                  var data = $.map($(this).select2('data'), function(value, key) {
                    return value.text ? '^' + $.fn.dataTable.util.escapeRegex(value.text) + '$' : null
                  })
                  //if no data selected use ""
                  if (data.length === 0) {
                    data = [""]
                  }
                  //join array into string with regex or (|)
                  var val = data.join('|')
                  //search for the option(s) selected
                  column.search(val ? val : '', true, false).draw()
                })
            column.data().unique().sort().each(function (d, j) {
              if (d === "") {
                return
              }
              select.append('<option value="'+d+'">'+d+'</option>');
            })
            //use column title as selector and placeholder
            $('#select_' + table_column.data + '_valid').select2({
              multiple: true,
              closeOnSelect: true,
              placeholder: "Filtrer " + (table_column.filter_title  ? table_column.filter_title : table_column.title),
              placeholderOption: function () { return undefined; }
            });
            //initially clear select otherwise first option is selected
            $('.select2').val(null).trigger('change')
          } else {
            $(column.footer()).append()
          }
        }).draw()
      }
    })
    $("#datatable_valid tbody").on('click', 'td', (e) => {
      display_producers_lot_modal(table_valid, table_columns_producers_validated, e)
    })
    window.table_valid = table_valid
    var producerValidTableSettings = loadTableSettings(table_columns_producers_validated, 'producerValidTableSettings')
    showHideTableColumns(table_valid, producerValidTableSettings, 'valid')
  } else {
    window.table_valid.draw()
  }
}

function init_datatables_operators_affiliations() {
  if (!$.fn.DataTable.isDataTable('#datatable_affiliations')) {

    let empty_footer = `<tr>${Array(table_columns_operators_affiliated.length).fill("<th></th>").join('')}</tr>`
    $("#datatable_affiliations tfoot").append(empty_footer)

    let table = $('#datatable_affiliations').DataTable({
      paging: false,
      info: false,
      scrollX: true,
      fixedColumns: {
      	leftColumns: 0,
        rightColumns: 1,
      },
      dom: 'rtip',
      columns: table_columns_operators_affiliated,
      columnDefs: [
        {
          className: "dt-center",
          targets: "_all",
        },
        {
          targets: 0,
          searchable:false,
          orderable:false,
          width:'1%',
          className: 'dt-body-center',
          render: function (data, type, full, meta) {
             return '<input type="checkbox">';
          }
        }
      ],
      order: [[ 1, 'asc' ]],
      ajax: {
        url: window.operators_api_affiliated_lots,
        dataSrc: function(json) {
          for (let i = 0, len = json.length; i < len; i++) {
            // add checkbox on the fly
            json[i]["checkbox"] = `<input type="checkbox" />`
          }
          return json
        }
      },
      initComplete: function() {
        // create filter
        this.api().columns().every(function () {
          var column = this;
          let table_column = table_columns_operators_affiliated[column.index()]
          if (table_column.can_filter === true) {
            var select = $('<select><option value=""></option></select>')
            .appendTo($(column.footer()).empty())
            .on('change', function() {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              column.search(val ? '^'+val+'$' : '', true, false).draw();
            });
            column.data().unique().sort().each(function (d, j) {
              select.append('<option value="'+d+'">'+d+'</option>')
            });
          } else {
            $(column.footer()).append()
          }
        }).draw()
      }
    })
    window.table_operators_affiliations = table
    $("#datatable_affiliations tbody").on('click', 'td', (e) => {
      display_operators_lot_modal(table, table_columns_operators_affiliated, e)
    })
    var operatorsAffiliationsTableSettings = loadTableSettings(table_columns_operators_affiliated, 'operatorsAffiliationsTableSettings')
    showHideTableColumns(table, operatorsAffiliationsTableSettings, 'affiliations')

    // Handle click on checkbox
    $('#datatable_affiliations tbody').on('click', 'input[type="checkbox"]', function(e) {
      var $row = $(this).closest('tr');
      // Get row data
      var rowId = table.row($row).index();
      // Determine whether row ID is in the list of selected row IDs
      var index = $.inArray(rowId, selected_rows);
      // If checkbox is checked and row ID is not in list of selected row IDs
      if(this.checked && index === -1) {
        selected_rows.push(rowId);
      // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
      } else if (!this.checked && index !== -1) {
        selected_rows.splice(index, 1);
      }
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
      // Prevent click event from propagating to parent
      e.stopPropagation();
      // Show/Hide buttons depending on selected_rows content
      manage_actions_operators_affiliation()
    })

    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table.table().container()).on('click', function(e) {
    	console.log(`thead checkbox click`)
      if (this.checked) {
      	console.log(`header checkbox checked`)
        $('#datatable_affiliations tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
      	console.log(`header checkbox unchecked`)
        $('#datatable_affiliations tbody input[type="checkbox"]:checked').trigger('click');
      }
      // Prevent click event from propagating to parent
      e.stopPropagation();
    });

  } else {
    window.table_operators_affiliations.draw()
  }
}

function init_datatables_operators_declared() {
  if (!$.fn.DataTable.isDataTable('#datatable_declared')) {

    let empty_footer = `<tr>${Array(table_columns_operators_declared.length).fill("<th></th>").join('')}</tr>`
    $("#datatable_declared tfoot").append(empty_footer)

    let table = $('#datatable_declared').DataTable({
      paging: false,
      info: false,
      scrollX: true,
      language: {
          search: "Rechercher:"
      },
      dom: 'rtip',
      columnDefs: [
      {"className": "dt-center", "targets": "_all"}
      ],
      columns: table_columns_operators_declared,
      ajax: {
        url: window.operators_api_declared_lots,
        dataSrc: function(json) {
          for (let i = 0, len = json.length; i < len; i++) {
            // add checkbox on the fly
            json[i]["checkbox"] = `<input type="checkbox" />`
          }
          return json
        }
      },
      initComplete: function() {
        // create filter
        this.api().columns().every(function () {
          var column = this;
          let table_column = table_columns_operators_declared[column.index()]
          if (table_column.can_filter === true) {
            var select = $('<select><option value=""></option></select>')
            .appendTo($(column.footer()).empty())
            .on('change', function() {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              column.search(val ? '^'+val+'$' : '', true, false).draw();
            });
            column.data().unique().sort().each(function (d, j) {
              select.append('<option value="'+d+'">'+d+'</option>')
            });
          } else {
            $(column.footer()).append()
          }
        }).draw()
      }
    })
    window.table_operators_declared = table
    $("#datatable_declared tbody").on('click', 'td', (e) => {
      display_operators_lot_modal(table, table_columns_operators_declared, e)
    })
    var operatorsValidTableSettings = loadTableSettings(table_columns_operators_declared, 'operatorsValidTableSettings')
    showHideTableColumns(table, operatorsValidTableSettings, 'declared')

    $('#input_search_datatable_valid').on('keyup', function() {
      table.search(this.value).draw();
    })

  } else {
    window.table_operators_declared.draw()
  }
}

function display_producers_lot_modal(table, columns, event) {
  // check if we clicked on the checkbox
  let colid = event.target._DT_CellIndex.column
  let rowid = event.target._DT_CellIndex.row
  let data = table.row(rowid).data()
  let table_column = columns[colid]
  let comments_section = $("#comments_section")
  comments_section.empty()
  if (table_column['data'] === 'checkbox') {
    // ignore clicks on checkbox column
    return
  } else {
    let modal = document.getElementById("modal_edit_lot")
    for (key in data) {
      // set the value in the field
      $(`#${key}`).val(data[key])
      // reset error field to none
      $(`#${key}_error`).html('')
    }

    // override errors into the field
    let lot_id = data['lot_id']
    if (lot_id in lot_errors) {
      let errors = lot_errors[lot_id]
      for (key in errors) {
        $(`#${key}`).val(errors[key])
      }
    }

    // non-input keys
    ['ghg_total', 'ghg_reduction'].forEach(function(item, index) {
      $(`#${item}`).html(data[item])
    })
    $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${data['ghg_reference']} gCO2eq/MJ`)

    /* load errors */
    $.ajax({url: window.producers_api_lot_errors,
      data: {'lot_id': data['lot_id'], 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
      type        : 'POST',
      success     : function(data, textStatus, jqXHR){
        // Callback code
        // load existing errors into the form
        for (let i = 0, len = data.length; i < len; i++) {
          let dom = $(`#${data[i].field}_error`)
          dom.html(`${data[i].error}`)
        }
      },
      error       : function(e) {
        if (e.status === 400) {
          alert(e.responseJSON.message)
          console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
        } else {
          alert("Server error. Please contact an administrator")
          console.log(`server error ${JSON.stringify(e)}`)
        }
      }
    })

    /* load comments */
    $.ajax({
      url         : window.producers_api_lot_comments,
      data        : {'lot_id': data['lot_id'], 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
      type        : 'POST',
      success     : function(d, textStatus, jqXHR){
        // Callback code
        // load existing comments into the form
        for (let i = 0, len = d.length; i < len; i++) {
          let c = d[i]
          let html = `<p><b>${c.from}</b>: ${c.comment}</p>`
          comments_section.append(html)
        }
        // add area to respond
        if (data['status'] === "Draft" || data['ea_delivery_status'] === "Accepté") {
          // do nothing
        } else {
          // add the ability to add a comment
          let html = `<div style="display: flex;"><p>Ajouter un commentaire:</p><input type="text" name="textarea" id="textarea" style="max-width: 80%; height: 2em; margin-left: 10px; margin-top: auto; margin-bottom: auto;" /></div>`
          comments_section.append(html)
        }
      },
      error       : function(e) {
        if (e.status === 400) {
          alert(e.responseJSON.message)
          console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
        } else {
          alert("Server error. Please contact an administrator")
          console.log(`server error ${JSON.stringify(e)}`)
        }
      }
    })

    /* warning if the lot is validated */
    if (data['status'] == 'Validated') {
      let message = `<h3>Lot ${data['carbure_id']}</h3>
      <h5 style="color: tomato">Attention, ce lot a déjà été déclaré à la DGEC et affilié à un client.</h5>
      <span>Toute modification leur sera automatiquement notifiée et devra être acceptée par le client.</span>`
      $("#err_msg_dom").html(message)
    } else {
      $("#err_msg_dom").html('')
    }
    modal.style.display = "flex"
  }
}

function display_operators_lot_modal(table, columns, event) {
  // check if we clicked on the checkbox
  if (event.target._DT_CellIndex === undefined) {
  	return
  }
  let colid = event.target._DT_CellIndex.column
  let rowid = event.target._DT_CellIndex.row
  let data = table.row(rowid).data()
  let table_column = columns[colid]

	let comments_section = $("#comments_section")
	let show_add_comment_section = $("#show_add_comment_section")
	let add_comment_section = $("#add_comment_section")
	let show_reject_section = $("#show_reject_section")
	let reject_section = $("#reject_section")
	show_reject_section.show()
	show_add_comment_section.show()
	add_comment_section.hide()
	comments_section.empty()
	comments_section.hide()
	reject_section.hide()

  if (table_column['data'] === 'checkbox') {
    // ignore clicks on checkbox column
    return
  } else {
    let modal = document.getElementById("modal_edit_lot")
    for (key in data) {
      // set the value in the field
      $(`#${key}`).val(data[key])
      // reset error field to none
      $(`#${key}_error`).html('')
    }

    // override errors into the field
    let lot_id = data['lot_id']
    if (lot_id in lot_errors) {
      let errors = lot_errors[lot_id]
      for (key in errors) {
        $(`#${key}`).val(errors[key])
      }
    }

    // non-input keys
    ['ghg_total', 'ghg_reduction'].forEach(function(item, index) {
      $(`#${item}`).html(data[item])
    })
    $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${data['ghg_reference']} gCO2eq/MJ`)

    /* load comments */
    $.ajax({
      url         : window.operators_api_lot_comments,
      data        : {'lot_id': data['lot_id'], 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
      type        : 'POST',
      success     : function(d, textStatus, jqXHR){
        // Callback code
        // load existing comments into the form
        for (let i = 0, len = d.length; i < len; i++) {
          let c = d[i]
          let html = `<p><b>${c.from}</b>: ${c.comment}</p>`
          comments_section.append(html)
        }
        if (d.length > 0) {
			comments_section.show()
        }
      },
      error       : function(e) {
        if (e.status === 400) {
          alert(e.responseJSON.message)
          console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
        } else {
          alert("Server error. Please contact an administrator")
          console.log(`server error ${JSON.stringify(e)}`)
        }
      }
    })

		if (data['ea_delivery_status'] == 'Accepté') {
			let message = `<h3>Lot ${data['carbure_id']}</h3>`
			$("#btn_lot_accept_final").hide()
			$("#err_msg_dom").html(message)
		} else {
			$("#err_msg_dom").html('')

	  	if (data['ea_delivery_status'] == 'Corrigé') {
				$("#btn_lot_accept_final").text("Accepter Définitivement")
			} else {
				$("#btn_lot_accept_final").text("Accepter Lot")
			}
			$("#btn_lot_accept_final").show()
		}
	  modal.style.display = "flex"
  }
}

function handleSave(action) {
  var err_msg_dom = $("#err_msg_dom")
  err_msg_dom.empty()
  var formdata = new FormData();
  formdata.set('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value)
  $(".modal-edit input").each(function() {
    formdata.set($(this).attr('id'), $(this).val())
  })

  // post form
  $.ajax({
    url         : window.producers_api_attestation_save_lot,
    data        : formdata,
    cache       : false,
    contentType : false,
    processData : false,
    type        : 'POST',
    success     : function(data, textStatus, jqXHR) {
      // Callback code
      // if there's an additional comment, save it as well
		  let comment = $("#textarea").val()
		  if (comment) {
		  	var formcomment = new FormData();
		  	formcomment.set('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value)
		  	formcomment.set('lot_id', document.getElementById('lot_id').value)
		  	formcomment.set('comment', comment)
			  $.ajax({
			    url         : window.producers_api_attestation_save_lot_comment,
			    data        : formcomment,
			    cache       : false,
			    contentType : false,
			    processData : false,
			    type        : 'POST',
			    success     : function(data, textStatus, jqXHR) {
			      // Callback code
			      window.location.reload()
			    },
			    error       : function(e) {
			      window.location.reload()
			      if (e.status === 400) {
			        err_msg_dom.html(`${e.responseJSON.message}`)
			      } else {
			        alert("Server error. Please contact an administrator")
			      }
			    }
			  })
			} else {
		        window.location.reload()
			}
    },
    error       : function(e) {
      if (e.status === 400) {
        err_msg_dom.html(`${e.responseJSON.message}`)
      } else {
        alert("Server error. Please contact an administrator")
      }
    }
  })
}


function load_ges(mp, bc) {
  $.ajax({
    url         : window.producers_api_ges + `?mp=${mp}&bc=${bc}`,
    cache       : false,
    contentType : false,
    processData : false,
    type        : 'GET',
    success     : function(data, textStatus, jqXHR) {
      // Callback code
      $.each(data, function(key, value) {
        $(`#${key}`).val(value)
      })
      $("#eec").change()
    },
    error       : function(e) {
      if (e.status === 400) {
        alert(e.responseJSON.message)
      } else {
        alert("Server error. Please contact an administrator")
      }
    }
  })
}

$(".ges_field").on('change', function() {
  var sum_incr = 0
  var sum_decr = 0
  var ref = parseFloat($("#ghg_reference").val())
  $(".ges_incr").each(function(index, elem) {
    sum_incr += parseFloat(elem.value)
  })
  $(".ges_decr").each(function(index, elem) {
    sum_decr += parseFloat(elem.value)
  })
  var sum = sum_incr - sum_decr
  $("#ghg_total").text(sum.toFixed(2))
  var pct_reduction = (1.0 - (sum / ref)) * 100
  $("#ghg_reduction").text(`${pct_reduction.toFixed(2)}%`)
  $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${ref} gCO2eq/MJ`)
})

$(document).ready(function() {
$(".autocomplete_mps").autocomplete({
  serviceUrl: window.producers_api_mps_autocomplete,
  dataType: 'json',
  minChars: 0,
  onSelect: function(suggestion) {
    $("#matiere_premiere_code").val(suggestion.data)
    let selected_bc = $("#biocarburant_code").val()
    if (selected_bc !== '') {
      load_ges(suggestion.data, selected_bc)
    }
  },
  onInvalidateSelection: function() {
    $("#matiere_premiere_code").val('')
  },
  showNoSuggestionNotice: true,
})

$(".autocomplete_biocarburants").autocomplete({
  serviceUrl: window.producers_api_biocarburants_autocomplete,
  dataType: 'json',
  minChars: 0,
  onSelect: function(suggestion) {
    $("#biocarburant_code").val(suggestion.data)
    let selected_mp = $("#matiere_premiere_code").val()
    if (selected_mp !== '') {
      load_ges(selected_mp, suggestion.data)
    }
  },
  onInvalidateSelection: function() {
    $("#biocarburant_code").val('')
  },
})

$(".autocomplete_production_sites").autocomplete({
  serviceUrl: window.producers_api_production_sites_autocomplete,
  dataType: 'json',
  minChars: 0,
})

$(".autocomplete_countries").autocomplete({
  serviceUrl: window.api_country_autocomplete,
  dataType: 'json',
  onSelect: function(suggestion) {
    $("#pays_origine_code").val(suggestion.data)
  },
  onInvalidateSelection: function() {
    $("#pays_origine_code").val('')
  }
})

$(".autocomplete_operators").autocomplete({
  serviceUrl: window.api_operators_autocomplete,
  dataType: 'json',
  minChars: 0,
})

$(".autocomplete_depots").autocomplete({
  serviceUrl: window.api_depots_autocomplete,
  dataType: 'json',
  minChars: 1,
  onSelect: function(suggestion) {
    $("#ea_delivery_site").val(suggestion.name)
  },
})

const dt_drafts_config = {
	id: "datatable_drafts",
	url: window.producers_api_lots_drafts_v2,
	col_definition: table_columns_drafts_v2,
	has_footer: true,
	paging: true,
	info: true,
	dom: 'rtp',
	columnDefs: [
    {
      targets: [0],
      searchable:false,
      orderable:false,
      width:'1%',
      className: 'dt-body-center',
      render: function (data, type, full, meta) {
        return '<input type="checkbox">';
      }
    },
    {
      className: "dt-center",
      targets: "_all",
      render: function (data, type, full, meta) {
      	let col_name = table_columns_drafts_v2[meta.col].data
      	if (table_columns_drafts_v2[meta.col]['render'] != undefined) {
  		return table_columns_drafts_v2[meta.col]['render'](full)
      	}
      	return full['fields'][col_name]
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: function(res) {
    data = {}
    lots = JSON.parse(res['lots'])
    for (let i = 0, len = lots.length; i < len; i++) {
    	let lot = lots[i]
    	data[lot.pk] = lot
    }
    txs = JSON.parse(res['transactions'])
    for (let i = 0, len = txs.length; i < len; i++) {
    	let tx = txs[i]
    	data[tx.fields.lot].tx = tx
    }
    list = Object.values(data)
    return list
  },
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_producers_lot_modal(table, table_columns_drafts_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })

    // Handle click on checkbox
    $(`#${tbl_id} tbody`).on('click', 'input[type="checkbox"]', function(e) {
      var $row = $(this).closest('tr');
      // Get row data
      var rowId = table.row($row).index();
      // Determine whether row ID is in the list of selected row IDs
      var index = $.inArray(rowId, selected_rows);
      // If checkbox is checked and row ID is not in list of selected row IDs
      if(this.checked && index === -1) {
        selected_rows.push(rowId);
      // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
      } else if (!this.checked && index !== -1) {
        selected_rows.splice(index, 1);
      }
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
      // Prevent click event from propagating to parent
      e.stopPropagation();
      // Show/Hide buttons depending on selected_rows content
      manage_actions()
    })


    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table.table().container()).on('click', function(e){
      if(this.checked){
         $('#datatable_drafts tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_drafts tbody input[type="checkbox"]:checked').trigger('click');
      }
      // Prevent click event from propagating to parent
      e.stopPropagation();
    });

    // Handle table draw event
    table.on('draw', function(){
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
    });
  }
}

const dt_received_config = {
	id: "datatable_received",
	url: window.producers_api_lots_received_v2,
	col_definition: table_columns_received_v2,
	has_footer: true,
	paging: true,
	info: true,
	dom: 'rtp',
	columnDefs: [
    {
      targets: [0],
      searchable:false,
      orderable:false,
      width:'1%',
      className: 'dt-body-center',
      render: function (data, type, full, meta) {
        return '<input type="checkbox">';
      }
    },
    {
      className: "dt-center",
      targets: "_all",
      render: function (data, type, full, meta) {
      	let col_name = table_columns_received_v2[meta.col].data
      	if (table_columns_received_v2[meta.col]['render'] != undefined) {
  		  return table_columns_received_v2[meta.col]['render'](full)
      	}
      	return full['fields'][col_name]
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: function(res) {
    data = {}
    lots = JSON.parse(res['lots'])
    for (let i = 0, len = lots.length; i < len; i++) {
    	let lot = lots[i]
    	data[lot.pk] = lot
    }
    txs = JSON.parse(res['transactions'])
    for (let i = 0, len = txs.length; i < len; i++) {
    	let tx = txs[i]
    	data[tx.fields.lot].tx = tx
    }
    list = Object.values(data)
    console.log(list)
    return list
  },
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_producers_lot_modal(table, table_columns_received_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })

    // Handle click on checkbox
    $(`#${tbl_id} tbody`).on('click', 'input[type="checkbox"]', function(e) {
      var $row = $(this).closest('tr');
      // Get row data
      var rowId = table.row($row).index();
      // Determine whether row ID is in the list of selected row IDs
      var index = $.inArray(rowId, selected_rows);
      // If checkbox is checked and row ID is not in list of selected row IDs
      if(this.checked && index === -1) {
        selected_rows.push(rowId);
      // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
      } else if (!this.checked && index !== -1) {
        selected_rows.splice(index, 1);
      }
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
      // Prevent click event from propagating to parent
      e.stopPropagation();
      // Show/Hide buttons depending on selected_rows content
      manage_actions()
    })


    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table.table().container()).on('click', function(e){
      if(this.checked){
         $('#datatable_drafts tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_drafts tbody input[type="checkbox"]:checked').trigger('click');
      }
      // Prevent click event from propagating to parent
      e.stopPropagation();
    });

    // Handle table draw event
    table.on('draw', function(){
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
    });
  }
}

const dt_errors_config = {
	id: "datatable_corrections",
	url: window.producers_api_lots_corrections_v2,
	col_definition: table_columns_corrections_v2,
	has_footer: true,
	paging: true,
	info: true,
	dom: 'rtp',
	columnDefs: [
    {
      className: "dt-center",
      targets: "_all",
      render: function (data, type, full, meta) {
      	let col_name = table_columns_corrections_v2[meta.col].data
      	if (table_columns_corrections_v2[meta.col]['render'] != undefined) {
  		return table_columns_corrections_v2[meta.col]['render'](full)
      	}
      	return full['fields'][col_name]
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: function(res) {
    data = {}
    lots = JSON.parse(res['lots'])
    for (let i = 0, len = lots.length; i < len; i++) {
    	let lot = lots[i]
    	data[lot.pk] = lot
    }
    txs = JSON.parse(res['transactions'])
    for (let i = 0, len = txs.length; i < len; i++) {
    	let tx = txs[i]
    	data[tx.fields.lot].tx = tx
    }
    list = Object.values(data)
    return list
  },
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_producers_lot_modal(table, table_columns_corrections_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
  }
}

const dt_valid_config = {
	id: "datatable_valid",
	url: window.producers_api_lots_valid_v2,
	col_definition: table_columns_valid_v2,
	has_footer: true,
	paging: true,
	info: true,
	dom: 'rtp',
	columnDefs: [
    {
      className: "dt-center",
      targets: "_all",
      render: function (data, type, full, meta) {
      	let col_name = table_columns_valid_v2[meta.col].data
      	if (table_columns_valid_v2[meta.col]['render'] != undefined) {
  		  return table_columns_valid_v2[meta.col]['render'](full)
      	}
      	return full['fields'][col_name]
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: function(res) {
    data = {}
    lots = JSON.parse(res['lots'])
    for (let i = 0, len = lots.length; i < len; i++) {
    	let lot = lots[i]
    	data[lot.pk] = lot
    }
    txs = JSON.parse(res['transactions'])
    for (let i = 0, len = txs.length; i < len; i++) {
    	let tx = txs[i]
    	data[tx.fields.lot].tx = tx
    }
    list = Object.values(data)
    return list
  },
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_producers_lot_modal(table, table_columns_valid_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
  }
}

dt_config['tab_drafts'] = dt_drafts_config
dt_config['tab_received'] = dt_received_config
dt_config['tab_errors'] = dt_errors_config
dt_config['tab_valid'] = dt_valid_config

})

// tab management v2
$(".tabs__tab").on('click', function() {
  // hide all
  console.log(`clicked on tab ${this.id}`)
  tabs = document.getElementsByClassName("tabcontent")
  for (let i = 0, len = tabs.length; i < len; i++) {
  	// hide tab content
  	if (tabs[i].id !== this.dataset.dst) {
  		tabs[i].style.display = "none";
  	} else {
  		tabs[i].style.display = "block";
  	}
  }
  // remove tab title style
  tabtitles = document.getElementsByClassName("tabs__tab")
  for (let i = 0, len = tabtitles.length; i < len; i++) {
  	tabtitles[i].className = tabtitles[i].className.replace(" tabs__tab--selected", "")
  }
  this.className = "tabs__tab tabs__tab--selected"

  init_datatables_generic(this.dataset.dst)
})


$("#btn_reject_with_comment").on('click', function() {
  let lot_id = $("#lot_id").val()
  let comment = $("#textarea_reject").val()
  $.ajax({
    url: window.operators_api_reject_with_comments,
    data: {'lots': lot_id, comment:comment, 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
    type        : 'POST',
    success     : function(data, textStatus, jqXHR){
      // Callback code
      window.location.reload()
    },
    error       : function(e) {
      if (e.status === 400) {
        alert(e.responseJSON.message)
        console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
      } else {
        alert("Server error. Please contact an administrator")
        console.log(`server error ${JSON.stringify(e)}`)
      }
    }
  })
})

$("#btn_accept_with_comment").on('click', function() {
  let lot_id = $("#lot_id").val()
  let comment = $("#producer_comment").val()
  $.ajax({
    url: window.operators_api_accept_with_comments,
    data: {'lot': lot_id,'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value,
           'comment': comment},
    type        : 'POST',
    success     : function(data, textStatus, jqXHR){
      // Callback code
      window.location.reload()
    },
    error       : function(e) {
      if (e.status === 400) {
        alert(e.responseJSON.message)
        console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
      } else {
        alert("Server error. Please contact an administrator")
        console.log(`server error ${JSON.stringify(e)}`)
      }
    }
  })
})


$("#show_add_comment_section").on('click', function() {
  $("#add_comment_section").show()
  $("#show_add_comment_section").hide()
})

$("#show_reject_section").on('click', function() {
  $("#reject_section").show()
  $("#show_reject_section").hide()
})

$("#add_lot").on('click', function() {
  let modal = document.getElementById("modal_edit_lot")
  /* empty all input fields */
  $("#modal_edit_lot input").each(function() {
    $(this).val('')
  })
  $("#err_msg_dom").html('')
  let non_input_fields = ['ghg_total', 'ghg_reduction']
  for (let i = 0, len = non_input_fields.length; i < len; i++) {
    let field = non_input_fields[i]
   $(`#${field}`).html('')
  }
  /* check if we have production sites, mps and bcs in parameters */
  check_production_sites()
  check_mps()
  check_biocarburants()
  $("#reduction_title").attr('title', '')
  modal.style.display = "flex"
})

function init_datatables_generic(tab_name) {
  const config = dt_config[tab_name]
  const tblselector = `#${config.id}`

  // tab Drafts
  if (!$.fn.DataTable.isDataTable(tblselector)) {
  	if (config.has_footer) {
  	  // create empty footer
      let empty_footer = `<tr>${Array(config.col_definition.length).fill("<th></th>").join('')}</tr>`
      $(`${tblselector} tfoot`).append(empty_footer)
  	}
    var table = $(tblselector).DataTable({
      paging: config.paging,
      info: config.info,
      dom: config.dom,
      scrollX: true,
      columnDefs: config.columnDefs,
      order: config.order,
      columns: config.col_definition,
      ajax: {
        url: config.url,
        dataSrc: config.ajax_dataSrc,
      },
    })
    if (config.post_init) {
      config.post_init(table)
    }
    window[config.id] = table
    window.table = table
    var producerDraftsTableSettingsV2 = loadTableSettings(config.col_definition, 'producerDraftsTableSettingsV2')
    showHideTableColumns(table, producerDraftsTableSettingsV2, 'drafts')
  } else {
    window[config.id].draw()
    window.table = window[config.id]
  }
}

$("#btn_lot_save").on('click', handleSave)

$("#btn_close_modal_import").on('click', () => {
  window.location.reload()
})

$("#btn_submit_upload_form").on('click', () => {
  $("#modal_import_form").submit()
})
