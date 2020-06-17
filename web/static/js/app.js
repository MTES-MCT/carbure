const dt_config = {}
const lot_errors = {}
const selected_rows = []
const received_selected_rows = []

const table_columns_drafts_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_producer ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_production_site ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_production_site ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.biocarburant ? full.fields.biocarburant.name : ''}},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.matiere_premiere ? full.fields.matiere_premiere.name : ''}},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.pays_origine ? full.fields.pays_origine.code_pays : '' }},

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
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.carbure_client ? full.tx.fields.carbure_client.name : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.carbure_delivery_site ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]

const table_columns_corrections_v2 = [
{title:'Période', can_hide: true, data:'period'},
{title:'Numéro de lot', can_hide: true, data:'carbure_id'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
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
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client.name : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
{title:'Status', can_hide: true, can_filter: true, orderable: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_status}},
]


const table_columns_received_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Numéro de lot', can_hide: true, data:'carbure_id'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Fournisseur', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.tx.fields.vendor_is_in_carbure ? full.tx.fields.carbure_vendor.name : `<i>${full.tx.fields.unknown_vendor}</i>` }},
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
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client.name : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
{title:'Status', can_hide: true, can_filter: true, orderable: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_status}},
]

const table_columns_mb_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Numéro de lot', can_hide: true, data:'carbure_id'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_producer ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', hidden: true, filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_production_site ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', hidden: true, filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_production_site ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.biocarburant.name }},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.matiere_premiere.name }},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.pays_origine ? full.fields.pays_origine.code_pays : '' }},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},

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

{title:'Référence', hidden:true, can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, tooltip: 'Champ libre - Référence client', render: (data, type, full, meta) => {return full.tx.fields.champ_libre}},
{title:'Site de stockage', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]

const table_columns_valid_v2 = [
{title:'Période', can_hide: true, can_export: true, render: (data, type, full, meta) => { return full.fields.period }},
{title:'ID', can_hide: true, can_export: true, render: (data, type, full, meta) => { return full.fields.carbure_id }},
{title:'Producteur', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', hidden:true, filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Fournisseur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.tx.fields.vendor_is_in_carbure ? full.tx.fields.carbure_vendor.name : `<i>${full.tx.fields.unknown_vendor}</i>` }},
{title:'Date d\'entrée<br /> en EA', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_date}},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client.name : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
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
]

const operators_table_columns_in_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
{title:'Site de<br /> Production', hidden: true, filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.name : `<i>${full.fields.unknown_production_site}</i>` }},
{title:'Pays de<br /> Production', hidden: true, filter_title: 'Pays Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => { return full.fields.production_site_is_in_carbure ? full.fields.carbure_production_site.country.code_pays : (full.fields.unknown_production_country ? full.fields.unknown_production_country.code_pays: "") }},
{title:'Fournisseur', can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.tx.fields.vendor_is_in_carbure ? full.tx.fields.carbure_vendor : `<i>${full.tx.fields.unknown_vendor}</i>` }},
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
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
{title:'Source', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.fields.status == 'Validated' ? 'Carbure' : 'Excel'} },
]

const operators_table_columns_mb_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
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
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client.name : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
]

const operators_table_columns_out_v2 = [
{title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', hidden: true, can_hide: true, can_duplicate: true, can_export: true, render: (data, type, full, meta) => { return full.fields.producer_is_in_carbure ? full.fields.carbure_producer.name : `<i>${full.fields.unknown_producer}</i>` }},
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
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.client_is_in_carbure ? full.tx.fields.carbure_client.name : `<i>${full.tx.fields.unknown_client}</i>`}},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, render: (data, type, full, meta) => {return full.tx.fields.delivery_site_is_in_carbure ? full.tx.fields.carbure_delivery_site.name : `<i>${full.tx.fields.unknown_delivery_site}</i>` }},
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
      	  err_msg_dom.html(data.errors)
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
      columns = []
      for (let i = 0, len = nb_columns; i < len; i++) {
        let coldef = table_columns[i]
        if (coldef.hidden == true) {
          columns.push(0)
        } else {
          columns.push(1)
        }
      }
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


function duplicate_lot(tx_id) {
  var formdata = new FormData();
  formdata.set('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value)
  formdata.set('tx_id', tx_id)
  $.ajax({
    url         : window.producers_api_lot_duplicate_v2,
    data        : formdata,
    type        : 'POST',
    processData : false,
    contentType : false,
    success     : function(data, textStatus, jqXHR){
      // Callback code
      window.table.ajax.reload()
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
        $("#modal_validate_lots_list").append(`<li>${rowdata.fields.producer_is_in_carbure ? rowdata.fields.carbure_producer.name : rowdata.fields.unknown_producer} - ${rowdata.fields.volume} - ${rowdata.fields.biocarburant.name} - ${rowdata.fields.matiere_premiere.name}</li>`)
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
        $("#modal_delete_lots_list").append(`<li>${rowdata.fields.producer_is_in_carbure ? rowdata.fields.carbure_producer.name : rowdata.fields.unknown_producer} - ${rowdata.fields.volume} - ${rowdata.fields.biocarburant.name} - ${rowdata.fields.matiere_premiere.name}</li>`)
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
    let tx_id = window.table.row(selected_rows[0]).data().tx.pk
    $("#duplicate_lot").attr("onclick", `duplicate_lot(${tx_id})`)
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

function manage_accept_button() {
  if (received_selected_rows.length > 0) {
    $("#btn_open_modal_accept_lots").addClass('primary')
    $("#btn_open_modal_accept_lots").css("pointer-events", "auto")
    $("#btn_open_modal_accept_lots").removeClass('secondary')
    $("#modal_accept_lots_list").empty()
    let to_accept = []
    for (let i = 0, len = received_selected_rows.length; i < len; i++) {
      let rowdata = window.table.row(received_selected_rows[i]).data()
      to_accept.push(rowdata.tx.pk)
      $("#modal_accept_lots_list").append(`<li>${rowdata.fields.producer_is_in_carbure ? rowdata.fields.carbure_producer.name : rowdata.fields.unknown_producer} - ${rowdata.fields.volume} - ${rowdata.fields.biocarburant.name} - ${rowdata.fields.matiere_premiere.name}</li>`)
      $("#modal_accept_lots_txids").val(to_accept.join(","))
    }
  } else {
    $("#btn_open_modal_accept_lots").addClass('secondary')
    $("#btn_open_modal_accept_lots").css("pointer-events", "none")
    $("#btn_open_modal_accept_lots").removeClass('primary')
    // cleanup validate modal
    $("#modal_accept_lots_list").empty()
  }
}


function manage_received_actions() {
  // bouton Accepter Lots
  manage_accept_button()
}


function manage_actions_operators() {
  // bouton Accepter Lots
  $("#modal_accept_lots_list").empty()
  if (selected_rows.length > 0) {
    $("#btn_open_modal_accept_lots").addClass('primary')
    $("#btn_open_modal_accept_lots").css("pointer-events", "auto")
    $("#btn_open_modal_accept_lots").removeClass('secondary')

	let to_accept = []
    for (let i = 0, len = selected_rows.length; i < len; i++) {
      let rowdata = window.table.row(selected_rows[i]).data()
      $("#modal_accept_lots_list").append(`<li>${rowdata.tx.fields.vendor_is_in_carbure ? rowdata.tx.fields.carbure_vendor : rowdata.tx.fields.unknown_vendor} - ${rowdata.fields.volume} - ${rowdata.fields.biocarburant.name} - ${rowdata.fields.matiere_premiere.name}</li>`)
      to_accept.push(rowdata.tx.pk)
      $("#modal_accept_lots_txs").val(to_accept.join(","))
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
  console.log(`initFilters ${dom}`)
  var table_columns_filter = $(`#table_columns_${dom}_filter`)
  var table_columns_filter2 = $(`#table_columns_${dom}_filter2`)
  var columns_filter_html = ""
  var columns_filter_html2 = ""
  for (let i = 0, len = table.length; i < len; i++) {
    let column = table[i]
    if (column.can_hide === true) {
      // use two columns
      if (i <= (len / 2)) {
        columns_filter_html += `<tr><td><input type="checkbox" id="checkbox_${dom}${i}" class="toggle-vis-${dom}" data-column="${i}"></td><td><label for="checkbox${i}" class="label-inline">${column.title}</label></td></tr>`
      } else {
        columns_filter_html2 += `<tr><td><input type="checkbox" id="checkbox_${dom}${i}" class="toggle-vis-${dom}" data-column="${i}"></td><td><label for="checkbox${i}" class="label-inline">${column.title}</label></td></tr>`
      }
    }
  }
  table_columns_filter.append(columns_filter_html)
  table_columns_filter2.append(columns_filter_html2)
	$(`.toggle-vis-${dom}`).on('click', function(e) {
		// Get the column API object
		let colid = $(this).attr('data-column')
		let table_columns = dt_config[dom].col_definition
		// Toggle the visibility
		let column = window.table.column(colid);
		var settings = loadTableSettings(table_columns, dom)
    // console.log(`toggling colid ${colid} dom ${dom} columns ${table_columns[colid]} current ${settings[colid]}`)
		settings[colid] = settings[colid] == 1 ? 0 : 1
		saveTableSettings(settings, dom)
		column.visible(!column.visible());
	})

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

function producer_is_in_carbure(bool) {
	if (bool) {
      $("input[name='producer_is_in_carbure']").filter("[value='yes']").prop("checked", true)
      $("#carbure_producer_name").show()
    	$("#carbure_producer_name_label").show()
      $("#carbure_production_site_name").show()
    	$("#carbure_production_site_name_label").show()

    	$("#unknown_producer_name").hide()
    	$("#unknown_producer_name_label").hide()
    	$("#unknown_production_site_name").hide()
    	$("#unknown_production_site_name_label").hide()
    	$("#unknown_production_site_country").hide()
    	$("#unknown_production_site_country_label").hide()
    	$("#unknown_production_site_reference").hide()
    	$("#unknown_production_site_reference_label").hide()
    	$("#unknown_production_site_dbl_counting").hide()
    	$("#unknown_production_site_dbl_counting_label").hide()
    	$("#unknown_production_site_com_date").hide()
    	$("#unknown_production_site_com_date_label").hide()
	} else {
      $("input[name='producer_is_in_carbure']").filter("[value='no']").prop("checked", true)
      $("#carbure_producer_name").hide()
    	$("#carbure_producer_name_label").hide()
      $("#carbure_production_site_name").hide()
    	$("#carbure_production_site_name_label").hide()

    	$("#unknown_producer_name").show()
    	$("#unknown_producer_name_label").show()
    	$("#unknown_production_site_name").show()
    	$("#unknown_production_site_name_label").show()
    	$("#unknown_production_site_country").show()
    	$("#unknown_production_site_country_label").show()
    	$("#unknown_production_site_reference").show()
    	$("#unknown_production_site_reference_label").show()
    	$("#unknown_production_site_dbl_counting").show()
    	$("#unknown_production_site_dbl_counting_label").show()
    	$("#unknown_production_site_com_date").show()
    	$("#unknown_production_site_com_date_label").show()
	}
}

function client_is_in_carbure(bool) {
  if (bool) {
    $("input[name='client_is_in_carbure']").filter("[value='yes']").prop("checked", true)
    $("#carbure_client_label").show()
    $("#carbure_client").show()
    $("#unknown_client_label").hide()
    $("#unknown_client").hide()
  } else {
    $("input[name='client_is_in_carbure']").filter("[value='no']").prop("checked", true)
    $("#carbure_client_label").hide()
    $("#carbure_client").hide()
    $("#unknown_client_label").show()
    $("#unknown_client").show()
  }
}

function delivery_site_is_in_carbure(bool) {
  if (bool) {
    $("input[name='delivery_site_is_in_carbure']").filter("[value='yes']").prop("checked", true)
    $("#carbure_delivery_site_label").show()
    $("#carbure_delivery_site").show()

    $("#unknown_delivery_site_label").hide()
    $("#unknown_delivery_site").hide()
    $("#unknown_delivery_site_country_label").hide()
    $("#unknown_delivery_site_country").hide()
  } else {
    $("input[name='delivery_site_is_in_carbure']").filter("[value='no']").prop("checked", true)
    $("#carbure_delivery_site_label").hide()
    $("#carbure_delivery_site").hide()

    $("#unknown_delivery_site_label").show()
    $("#unknown_delivery_site").show()
    $("#unknown_delivery_site_country_label").show()
    $("#unknown_delivery_site_country").show()
  }
}

$('input[type=radio][name=producer_is_in_carbure][value=yes]').change(function() {
  producer_is_in_carbure(true)
})
$('input[type=radio][name=producer_is_in_carbure][value=no]').change(function() {
  producer_is_in_carbure(false)
})

$('input[type=radio][name=client_is_in_carbure][value=yes]').change(function() {
  client_is_in_carbure(true)
})
$('input[type=radio][name=client_is_in_carbure][value=no]').change(function() {
  client_is_in_carbure(false)
})

$('input[type=radio][name=delivery_site_is_in_carbure][value=yes]').change(function() {
  delivery_site_is_in_carbure(true)
})
$('input[type=radio][name=delivery_site_is_in_carbure][value=no]').change(function() {
  delivery_site_is_in_carbure(false)
})

function display_producers_lot_draft_modal(table, columns, event) {
  // check if we clicked on the checkbox
  let colid = event.target._DT_CellIndex.column
  let rowid = event.target._DT_CellIndex.row
  let data = table.row(rowid).data()
  let table_column = columns[colid]
  let comments_section = $("#comments_section")
  comments_section.empty()
  $("#btn_close_modal_lot_save").on('click', function() {
    let modal = document.getElementById('modal_lot')
    modal.style.display = 'none';
  })

  if (table_column['data'] === 'checkbox') {
    // ignore clicks on checkbox column
    return
  } else {
    let modal = document.getElementById("modal_lot")
    console.log(data)
    $("#save_section").show()
    $("#check_section").hide()
    $("#correct_section").hide()
    $("#lot_id").val(data.pk)
    $("#tx_id").val(data.tx.pk)

    if (data.fields.producer_is_in_carbure) {
    	producer_is_in_carbure(true)
    } else {
    	producer_is_in_carbure(false)
    }

    $("#carbure_producer_name").val(data.fields.carbure_producer ? data.fields.carbure_producer.name : '')
    $("#carbure_producer_id").val(data.fields.carbure_producer ? data.fields.carbure_producer.id : '')
    if (data.errors['producer']) {
      $("#carbure_producer_name_error").val(data.errors['producer'])
    }
    $("#carbure_production_site_name").val(data.fields.carbure_production_site ? data.fields.carbure_production_site.name : '')
    $("#carbure_production_site_id").val(data.fields.carbure_production_site ? data.fields.carbure_production_site.id : '')
    if (data.errors['production_site']) {
      $("#carbure_production_site_name_error").val(data.errors['production_site'])
    }
    $("#unknown_producer_name").val(data.fields.unknown_producer)
    $("#unknown_production_site_name").val(data.fields.unknown_production_site)
    $("#unknown_production_site_country").val(data.fields.unknown_production_country ? data.fields.unknown_production_country.name : '')
    $("#unknown_production_site_country_code").val(data.fields.unknown_production_country ? data.fields.unknown_production_country.code_pays : '')

    $("#unknown_production_site_com_date").val(data.fields.unknown_production_site_com_date)
    $("#unknown_production_site_reference").val(data.fields.unknown_production_site_reference)
    $("#unknown_production_site_dbl_counting").val(data.fields.unknown_production_site_dbl_counting)



    $("#volume").val(data.fields.volume)
    if (data.errors['volume']) {
      $("#volume_error").val(data.errors.volume)
    }
    $("#biocarburant").val(data.fields.biocarburant ? data.fields.biocarburant.name : '')
    $("#biocarburant_code").val(data.fields.biocarburant ? data.fields.biocarburant.code : '')
    if (data.errors['biocarburant']) {
      $("#biocarburant_error").val(data.errors.biocarburant)
    }
    $("#matiere_premiere").val(data.fields.matiere_premiere ? data.fields.matiere_premiere.name : '')
    $("#matiere_premiere_code").val(data.fields.matiere_premiere ? data.fields.matiere_premiere.code : '')
    if (data.errors['matiere_premiere']) {
      $("#matiere_premiere_error").val(data.errors.matiere_premiere)
    }
    $("#pays_origine").val(data.fields.pays_origine ? data.fields.pays_origine.name : '')
    $("#pays_origine_code").val(data.fields.pays_origine ? data.fields.pays_origine.code_pays : '')
    if (data.errors['pays_origine']) {
      $("#pays_origine_error").val(data.errors.pays_origine)
    }
    /* TX Related fields */
    $("#dae").val(data.tx.fields.dae)
    if (data.errors['dae']) {
      $("#dae_error").val(data.errors.dae)
    }

    if (data.tx.fields.client_is_in_carbure) {
      client_is_in_carbure(true)
    } else {
      client_is_in_carbure(false)
    }
    if (data.tx.fields.delivery_site_is_in_carbure) {
      delivery_site_is_in_carbure(true)
    } else {
      delivery_site_is_in_carbure(false)
    }

    $("#carbure_client").val(data.tx.fields.carbure_client ? data.tx.fields.carbure_client.name : '')
    $("#carbure_client_id").val(data.tx.fields.carbure_client ? data.tx.fields.carbure_client.id : '')
    if (data.errors['client']) {
      $("#carbure_client_error").val(data.errors.client)
    }
    $("#carbure_delivery_site").val(data.tx.fields.carbure_delivery_site ? data.tx.fields.carbure_delivery_site.name : '')
    $("#carbure_delivery_site_id").val(data.tx.fields.carbure_delivery_site ? data.tx.fields.carbure_delivery_site.depot_id : '')
    if (data.errors['delivery_site']) {
      $("#carbure_delivery_site_error").val(data.errors.delivery_site)
    }
    $("#unknown_client").val(data.tx.fields.unknown_client)
    $("#unknown_delivery_site").val(data.tx.fields.unknown_delivery_site)
    $("#unknown_delivery_site_country").val(data.tx.fields.unknown_delivery_site_country ? data.tx.fields.unknown_delivery_site_country.name : '')
    $("#unknown_delivery_site_country_code").val(data.tx.fields.unknown_delivery_site_country ? data.tx.fields.unknown_delivery_site_country.code_pays : '')
    $("#delivery_date").val(data.tx.fields.delivery_date)
    if (data.errors['delivery_date']) {
      $("#delivery_date_error").val(data.errors.delivery_date)
    }
    $("#champ_libre").val(data.tx.fields.champ_libre)

    /* Greenhouse gases values */
    $("#eec").val(data.fields.eec)
    $("#el").val(data.fields.el)
    $("#ep").val(data.fields.ep)
    $("#etd").val(data.fields.etd)
    $("#eu").val(data.fields.eu)
    $("#esca").val(data.fields.esca)
    $("#eccs").val(data.fields.eccs)
    $("#eccr").val(data.fields.eccr)
    $("#eee").val(data.fields.eee)

    // non-input keys
    $("#ghg_total").html(data.fields.ghg_total)
    $("#ghg_reduction").html(`${data.fields.ghg_reduction}%`)
    $("#ghg_reference").val(data.fields.ghg_reference)
    $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${data.fields.ghg_reference} gCO2eq/MJ`)

    /* load errors */
    /*
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
    })*/

    /* load comments */
    /*
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
    })*/

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

function display_producers_lot_received_modal(table, columns, event) {
  // check if we clicked on the checkbox
  let colid = event.target._DT_CellIndex.column
  let rowid = event.target._DT_CellIndex.row
  let data = table.row(rowid).data()
  let table_column = columns[colid]
  let comments_section = $("#comments_section")
  comments_section.empty()
  $("#btn_close_modal_lot_check").on('click', function() {
    let modal = document.getElementById('modal_lot')
    modal.style.display = 'none';
  })


  if (table_column['data'] === 'checkbox') {
    // ignore clicks on checkbox column
    return
  } else {
    let modal = document.getElementById("modal_lot")
    console.log(data)
    $("#save_section").hide()
    $("#correct_section").hide()
    $("#check_section").show()
    $("#lot_id").val(data.pk)
    $("#tx_id").val(data.tx.pk)

    if (data.fields.producer_is_in_carbure) {
    	producer_is_in_carbure(true)
    } else {
    	producer_is_in_carbure(false)
    }

    $("#carbure_producer_name").val(data.fields.carbure_producer ? data.fields.carbure_producer.name : '')
    $("#carbure_producer_id").val(data.fields.carbure_producer ? data.fields.carbure_producer.id : '')
    $("#carbure_production_site_name").val(data.fields.carbure_production_site ? data.fields.carbure_production_site.name : '')
    $("#carbure_production_site_id").val(data.fields.carbure_production_site ? data.fields.carbure_production_site.id : '')
    $("#unknown_producer_name").val(data.fields.unknown_producer)
    $("#unknown_production_site_name").val(data.fields.unknown_production_site)
    $("#unknown_production_site_country").val(data.fields.unknown_production_country ? data.fields.unknown_production_country.name : '')
    $("#unknown_production_site_country_code").val(data.fields.unknown_production_country ? data.fields.unknown_production_country.code_pays : '')

    $("#unknown_production_site_com_date").val(data.fields.unknown_production_site_com_date)
    $("#unknown_production_site_reference").val(data.fields.unknown_production_site_reference)
    $("#unknown_production_site_dbl_counting").val(data.fields.unknown_production_site_dbl_counting)



    $("#volume").val(data.fields.volume)
    $("#biocarburant").val(data.fields.biocarburant ? data.fields.biocarburant.name : '')
    $("#biocarburant_code").val(data.fields.biocarburant ? data.fields.biocarburant.code : '')
    $("#matiere_premiere").val(data.fields.matiere_premiere ? data.fields.matiere_premiere.name : '')
    $("#matiere_premiere_code").val(data.fields.matiere_premiere ? data.fields.matiere_premiere.code : '')
    $("#pays_origine").val(data.fields.pays_origine ? data.fields.pays_origine.name : '')
    $("#pays_origine_code").val(data.fields.pays_origine ? data.fields.pays_origine.code_pays : '')
    /* TX Related fields */
    $("#dae").val(data.tx.fields.dae)

    if (data.tx.fields.client_is_in_carbure) {
      client_is_in_carbure(true)
    } else {
      client_is_in_carbure(false)
    }
    if (data.tx.fields.delivery_site_is_in_carbure) {
      delivery_site_is_in_carbure(true)
    } else {
      delivery_site_is_in_carbure(false)
    }

    $("#carbure_client").val(data.tx.fields.carbure_client ? data.tx.fields.carbure_client.name : '')
    $("#carbure_client_id").val(data.tx.fields.carbure_client ? data.tx.fields.carbure_client.id : '')
    $("#carbure_delivery_site").val(data.tx.fields.carbure_delivery_site ? data.tx.fields.carbure_delivery_site.name : '')
    $("#carbure_delivery_site_id").val(data.tx.fields.carbure_delivery_site ? data.tx.fields.carbure_delivery_site.depot_id : '')
    $("#unknown_client").val(data.tx.fields.unknown_client)
    $("#unknown_delivery_site").val(data.tx.fields.unknown_delivery_site)
    $("#unknown_delivery_site_country").val(data.tx.fields.unknown_delivery_site_country ? data.tx.fields.unknown_delivery_site_country.name : '')
    $("#unknown_delivery_site_country_code").val(data.tx.fields.unknown_delivery_site_country ? data.tx.fields.unknown_delivery_site_country.code_pays : '')
    $("#delivery_date").val(data.tx.fields.delivery_date)
    $("#champ_libre").val(data.tx.fields.champ_libre)

    /* Greenhouse gases values */
    $("#eec").val(data.fields.eec)
    $("#el").val(data.fields.el)
    $("#ep").val(data.fields.ep)
    $("#etd").val(data.fields.etd)
    $("#eu").val(data.fields.eu)
    $("#esca").val(data.fields.esca)
    $("#eccs").val(data.fields.eccs)
    $("#eccr").val(data.fields.eccr)
    $("#eee").val(data.fields.eee)

    // non-input keys
    $("#ghg_total").html(data.fields.ghg_total)
    $("#ghg_reduction").html(`${data.fields.ghg_reduction}%`)
    $("#ghg_reference").val(data.fields.ghg_reference)
    $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${data.fields.ghg_reference} gCO2eq/MJ`)

    /* load comments */
    /*
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
    })*/
    modal.style.display = "flex"
  }
}

function display_producers_lot_correction_modal(table, columns, event) {
  // check if we clicked on the checkbox
  let colid = event.target._DT_CellIndex.column
  let rowid = event.target._DT_CellIndex.row
  let data = table.row(rowid).data()
  let table_column = columns[colid]
  let comments_section = $("#comments_section")
  comments_section.empty()
  $("#btn_close_modal_lot_correct").on('click', function() {
    let modal = document.getElementById('modal_lot')
    modal.style.display = 'none';
  })

  if (table_column['data'] === 'checkbox') {
    // ignore clicks on checkbox column
    return
  } else {
    let modal = document.getElementById("modal_lot")
    console.log(data)
    $("#save_section").hide()
    $("#check_section").hide()
    $("#correct_section").show()
    $("#lot_id").val(data.pk)
    $("#tx_id").val(data.tx.pk)

    if (data.fields.producer_is_in_carbure) {
      producer_is_in_carbure(true)
    } else {
      producer_is_in_carbure(false)
    }

    $("#carbure_producer_name").val(data.fields.carbure_producer ? data.fields.carbure_producer.name : '')
    $("#carbure_producer_id").val(data.fields.carbure_producer ? data.fields.carbure_producer.id : '')
    $("#carbure_production_site_name").val(data.fields.carbure_production_site ? data.fields.carbure_production_site.name : '')
    $("#carbure_production_site_id").val(data.fields.carbure_production_site ? data.fields.carbure_production_site.id : '')
    $("#unknown_producer_name").val(data.fields.unknown_producer)
    $("#unknown_production_site_name").val(data.fields.unknown_production_site)
    $("#unknown_production_site_country").val(data.fields.unknown_production_country ? data.fields.unknown_production_country.name : '')
    $("#unknown_production_site_country_code").val(data.fields.unknown_production_country ? data.fields.unknown_production_country.code_pays : '')

    $("#unknown_production_site_com_date").val(data.fields.unknown_production_site_com_date)
    $("#unknown_production_site_reference").val(data.fields.unknown_production_site_reference)
    $("#unknown_production_site_dbl_counting").val(data.fields.unknown_production_site_dbl_counting)



    $("#volume").val(data.fields.volume)
    $("#biocarburant").val(data.fields.biocarburant ? data.fields.biocarburant.name : '')
    $("#biocarburant_code").val(data.fields.biocarburant ? data.fields.biocarburant.code : '')
    $("#matiere_premiere").val(data.fields.matiere_premiere ? data.fields.matiere_premiere.name : '')
    $("#matiere_premiere_code").val(data.fields.matiere_premiere ? data.fields.matiere_premiere.code : '')
    $("#pays_origine").val(data.fields.pays_origine ? data.fields.pays_origine.name : '')
    $("#pays_origine_code").val(data.fields.pays_origine ? data.fields.pays_origine.code_pays : '')
    /* TX Related fields */
    $("#dae").val(data.tx.fields.dae)

    if (data.tx.fields.client_is_in_carbure) {
      client_is_in_carbure(true)
    } else {
      client_is_in_carbure(false)
    }
    if (data.tx.fields.delivery_site_is_in_carbure) {
      delivery_site_is_in_carbure(true)
    } else {
      delivery_site_is_in_carbure(false)
    }


    $("#carbure_client").val(data.tx.fields.carbure_client ? data.tx.fields.carbure_client.name : '')
    $("#carbure_client_id").val(data.tx.fields.carbure_client ? data.tx.fields.carbure_client.id : '')
    $("#carbure_delivery_site").val(data.tx.fields.carbure_delivery_site ? data.tx.fields.carbure_delivery_site.name : '')
    $("#carbure_delivery_site_id").val(data.tx.fields.carbure_delivery_site ? data.tx.fields.carbure_delivery_site.depot_id : '')
    $("#unknown_client").val(data.tx.fields.unknown_client)
    $("#unknown_delivery_site").val(data.tx.fields.unknown_delivery_site)
    $("#unknown_delivery_site_country").val(data.tx.fields.unknown_delivery_site_country ? data.tx.fields.unknown_delivery_site_country.name : '')
    $("#unknown_delivery_site_country_code").val(data.tx.fields.unknown_delivery_site_country ? data.tx.fields.unknown_delivery_site_country.code_pays : '')
    $("#delivery_date").val(data.tx.fields.delivery_date)
    $("#champ_libre").val(data.tx.fields.champ_libre)

    /* Greenhouse gases values */
    $("#eec").val(data.fields.eec)
    $("#el").val(data.fields.el)
    $("#ep").val(data.fields.ep)
    $("#etd").val(data.fields.etd)
    $("#eu").val(data.fields.eu)
    $("#esca").val(data.fields.esca)
    $("#eccs").val(data.fields.eccs)
    $("#eccr").val(data.fields.eccr)
    $("#eee").val(data.fields.eee)

    // non-input keys
    $("#ghg_total").html(data.fields.ghg_total)
    $("#ghg_reduction").html(`${data.fields.ghg_reduction}%`)
    $("#ghg_reference").val(data.fields.ghg_reference)
    $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${data.fields.ghg_reference} gCO2eq/MJ`)

    /* load comments */
    /*
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
    })*/
    modal.style.display = "flex"
  }
}

function handleSave(action) {
  var err_msg_dom = $("#err_msg_dom")
  err_msg_dom.empty()
  var formdata = new FormData();
  formdata.set('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value)
  $(".modal-edit input").each(function() {
    if ($(this).attr('id') !== undefined) {
      formdata.set($(this).attr('id'), $(this).val())
    }
  })
  formdata.set("producer_is_in_carbure", document.querySelector('input[name="producer_is_in_carbure"]:checked').value)
  formdata.set("client_is_in_carbure", document.querySelector('input[name="client_is_in_carbure"]:checked').value)
  formdata.set("delivery_site_is_in_carbure", document.querySelector('input[name="delivery_site_is_in_carbure"]:checked').value)

  // post form
  $.ajax({
    url         : window.producers_api_lot_save_v2,
    data        : formdata,
    cache       : false,
    contentType : false,
    processData : false,
    type        : 'POST',
    success     : function(data, textStatus, jqXHR) {
      // Callback code
      // if there's an additional comment, save it as well
      console.log(`handleSave res: ${data}`)
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
  console.log(`ref ${ref} sum ${sum}`)
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

$(".autocomplete_producers").autocomplete({
  serviceUrl: window.producers_api_producers_autocomplete_v2,
  dataType: 'json',
  minChars: 0,
  onSelect: function(suggestion) {
    $("#carbure_producer_id").val(suggestion.id)
    $("#carbure_producer_name").val(suggestion.value)
  },
  onInvalidateSelection: function() {
    $("#carbure_producer_id").val('')
    $("#carbure_producer_name").val('')
  }
})

$(".autocomplete_production_sites").autocomplete({
  serviceUrl: window.producers_api_production_sites_autocomplete,
  dataType: 'json',
  minChars: 0,
  onSelect: function(suggestion) {
    $("#carbure_production_site_id").val(suggestion.data)
  },
  onInvalidateSelection: function() {
    $("#carbure_production_site_id").val('')
  }
})

$(".autocomplete_countries").autocomplete({
  serviceUrl: window.api_country_autocomplete,
  dataType: 'json',
  onSelect: function(suggestion) {
    $(`#${this.id}_code`).val(suggestion.data)
  },
  onInvalidateSelection: function() {
    $(`#${this.id}_code`).val('')
  }
})

$(".autocomplete_clients").autocomplete({
  serviceUrl: window.producers_api_clients_autocomplete_v2,
  dataType: 'json',
  minChars: 0,
  onSelect: function(suggestion) {
    $("#carbure_client_id").val(suggestion.id)
  },
  onInvalidateSelection: function() {
    $("#carbure_client_id").val('')
  }
})

$(".autocomplete_depots").autocomplete({
  serviceUrl: window.producers_api_depots_autocomplete_v2,
  dataType: 'json',
  minChars: 0,
  onSelect: function(suggestion) {
    $("#carbure_delivery_site").val(suggestion.name)
    $("#carbure_delivery_site_id").val(suggestion.depot_id)
  },
  onInvalidateSelection: function() {
    $("#carbure_delivery_site").val('')
    $("#carbure_delivery_site_id").val('')
  }
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
    	data[lot.pk].errors = {}
    }
    txs = JSON.parse(res['transactions'])
    for (let i = 0, len = txs.length; i < len; i++) {
    	let tx = txs[i]
    	data[tx.fields.lot].tx = tx
    }
    errors = JSON.parse(res['errors'])
    for (let i = 0, len = errors.length; i < len; i++) {
      let error = errors[i]
      data[error.fields.lot].errors[error.field] = error
    }
    list = Object.values(data)
    return list
  },
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_producers_lot_draft_modal(table, table_columns_drafts_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(table_columns_drafts_v2, "tab_drafts")

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
    manage_actions()
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
    return list
  },
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_producers_lot_received_modal(table, table_columns_received_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(table_columns_received_v2, "tab_received")

    // Handle click on checkbox
    $(`#${tbl_id} tbody`).on('click', 'input[type="checkbox"]', function(e) {
      var $row = $(this).closest('tr');
      // Get row data
      var rowId = table.row($row).index();
      // Determine whether row ID is in the list of selected row IDs
      var index = $.inArray(rowId, received_selected_rows);
      // If checkbox is checked and row ID is not in list of selected row IDs
      if(this.checked && index === -1) {
        received_selected_rows.push(rowId);
      // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
      } else if (!this.checked && index !== -1) {
        received_selected_rows.splice(index, 1);
      }
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
      // Prevent click event from propagating to parent
      e.stopPropagation();
      // Show/Hide buttons depending on selected_rows content
      manage_received_actions()
    })


    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table.table().container()).on('click', function(e){
      if(this.checked){
         $('#datatable_received tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_received tbody input[type="checkbox"]:checked').trigger('click');
      }
      // Prevent click event from propagating to parent
      e.stopPropagation();
    });

    // Handle table draw event
    table.on('draw', function(){
      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);
    });
    manage_received_actions()
  }
}

const dt_mb_config = {
	id: "datatable_mb",
	url: window.producers_api_lots_mb_v2,
	col_definition: table_columns_mb_v2,
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
      	let col_name = table_columns_mb_v2[meta.col].data
      	if (table_columns_mb_v2[meta.col]['render'] != undefined) {
  		  return table_columns_mb_v2[meta.col]['render'](full)
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
      display_producers_lot_modal(table, table_columns_mb_v2, e)
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(table_columns_mb_v2, "tab_mb")

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
         $('#datatable_received tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_received tbody input[type="checkbox"]:checked').trigger('click');
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
      display_producers_lot_correction_modal(table, table_columns_corrections_v2, e)
    })
    initFilters(table_columns_corrections_v2, "tab_errors")

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
    initFilters(table_columns_valid_v2, "tab_valid")
  }
}

const dt_operators_in_config = {
	id: "datatable_in",
	url: window.operators_api_lots_in_v2,
	col_definition: operators_table_columns_in_v2,
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
      	let col_name = operators_table_columns_in_v2[meta.col].data
      	if (operators_table_columns_in_v2[meta.col]['render'] != undefined) {
  		  return operators_table_columns_in_v2[meta.col]['render'](full)
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
      display_producers_lot_modal(table, operators_table_columns_in_v2, e)
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
      manage_actions_operators()
    })

    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table.table().container()).on('click', function(e){
      if(this.checked){
         $('#datatable_in tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_in tbody input[type="checkbox"]:checked').trigger('click');
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

const dt_operators_mb_config = {
	id: "datatable_mb",
	url: window.operators_api_lots_mb_v2,
	col_definition: operators_table_columns_mb_v2,
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
      	let col_name = operators_table_columns_mb_v2[meta.col].data
      	if (operators_table_columns_mb_v2[meta.col]['render'] != undefined) {
  		  return operators_table_columns_mb_v2[meta.col]['render'](full)
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
      display_producers_lot_modal(table, operators_table_columns_mb_v2, e)
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
         $('#datatable_mb tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_mb tbody input[type="checkbox"]:checked').trigger('click');
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

const dt_operators_out_config = {
	id: "datatable_out",
	url: window.operators_api_lots_out_v2,
	col_definition: operators_table_columns_out_v2,
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
      	let col_name = operators_table_columns_out_v2[meta.col].data
      	if (operators_table_columns_out_v2[meta.col]['render'] != undefined) {
  		  return operators_table_columns_out_v2[meta.col]['render'](full)
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
      display_producers_lot_modal(table, operators_table_columns_out_v2, e)
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
         $('#datatable_out tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#datatable_out tbody input[type="checkbox"]:checked').trigger('click');
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

dt_config['tab_drafts'] = dt_drafts_config
dt_config['tab_received'] = dt_received_config
dt_config['tab_errors'] = dt_errors_config
dt_config['tab_mb'] = dt_mb_config
dt_config['tab_valid'] = dt_valid_config
dt_config['tab_operators_in'] = dt_operators_in_config
dt_config['tab_operators_mb'] = dt_operators_mb_config
dt_config['tab_operators_out'] = dt_operators_out_config

})

// tab management v2
$(".tabs__tab").on('click', function() {
  // hide all
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

$("#btn_accept_lot").on('click', function() {
  let tx_id = $("#tx_id").val()
  $.ajax({
    url: window.producers_api_lot_accept_v2,
    data: {'tx_id': tx_id, 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
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

$("#btn_reject_with_comment").on('click', function() {
  let tx_id = $("#tx_id").val()
  let comment = $("#textarea_reject").val()
  $.ajax({
    url: window.producers_api_lot_reject_v2,
    data: {'tx_id': tx_id, comment:comment, 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
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
  let tx_id = $("#tx_id").val()
  let comment = $("#textarea_correction").val()
  $.ajax({
    url: window.producers_api_lot_accept_with_correction_v2,
    data: {'tx_id': tx_id, comment: comment, 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value,
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
  let modal = document.getElementById("modal_lot")
  $("#check_section").hide()
  $("#correct_section").hide()
  $("#save_section").show()


  /* empty all input fields */
  $("#modal_lot input").each(function() {
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
    var tablesettings = loadTableSettings(config.col_definition, tab_name)
    showHideTableColumns(table, tablesettings, tab_name)
  } else {
    window[config.id].draw()
    window.table = window[config.id]
  }
}

$("#btn_lot_save").on('click', handleSave)

$("#btn_close_modal_import").on('click', () => {
  window.location.reload()
})

$("#btn_close_modal_accept_lots").on('click', () => {
  window.location.reload()
})

$("#btn_submit_upload_form").on('click', () => {
  $("#modal_import_form").submit()
})



