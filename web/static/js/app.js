const dt_config = {}
const lot_errors = {}
const selected_drafts = []
const selected_in = []
const selected_mb_drafts = []
const selected_mb = []

const columns_definitions = {
'checkbox': {title:'<input name="select_all" value="1" type="checkbox">', can_hide: false, read_only: true, render: (data, type, full, meta) => { return '<td><input type="checkbox" /></td>'}} ,
'id': {title:'ID', hidden:true, can_hide: true, read_only: true, render: (data, type, full, meta) => { return full.pk }} ,
'period': {title:'Période', hidden:true, can_hide: true, read_only: true, render: (data, type, full, meta) => { return full.fields.lot.period }} ,
'carbure_id': {title:'Numéro de lot', hidden:true, can_hide: true, read_only: true, render: (data, type, full, meta) => { return full.fields.lot.carbure_id }},
'lot_source': {title:'Lot Source', hidden:true, can_hide: true, read_only: true, render: (data, type, full, meta) => { return full.fields.lot.parent_lot.carbure_id }},
'producer': {title:'Producteur', hidden: true, can_filter: true, filter_title: 'Producteur', can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.carbure_producer ? full.fields.lot.carbure_producer.name : full.fields.lot.unknown_producer }},
'production_site': {title:'Site de<br /> Production', can_filter: true, filter_title: 'Site', can_hide: true, can_filter: true, orderable: false, render: (data, type, full, meta) => { return full.fields.lot.carbure_production_site ? full.fields.lot.carbure_production_site.name : full.fields.lot.unknown_production_site }},
'production_country': {title:'Pays de<br /> Production', filter_title: 'Pays Production', can_hide: true, can_filter: true, orderable: false, render: (data, type, full, meta) => { return full.fields.lot.carbure_production_site ? full.fields.lot.carbure_production_site.country.code_pays : (full.fields.lot.unknown_production_country ? full.fields.lot.unknown_production_country.code_pays: "") }},
'ps_com_date': {title:'Date de mise en service', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.carbure_production_site ? full.fields.lot.carbure_production_site.date_mise_en_service : full.fields.lot.unknown_production_site_com_date }},
'ps_ref': {title:'Référence sys. fournisseur', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.carbure_production_site ? full.fields.lot.carbure_production_site.name : full.fields.lot.unknown_production_site_reference }},
'ps_dbl': {title:'Num. double compte', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.carbure_production_site ? full.fields.lot.carbure_production_site.dc_reference : full.fields.lot.unknown_production_site_dbl_counting }},

'volume': {title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.volume }},
'biocarburant': {title:'Biocarburant', can_hide: true, can_filter: true, render: (data, type, full, meta) => { return full.fields.lot.biocarburant ? full.fields.lot.biocarburant.name : ''}},
'matiere_premiere': {title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_filter: true, render: (data, type, full, meta) => { return full.fields.lot.matiere_premiere ? full.fields.lot.matiere_premiere.name : ''}},
'pays_origine': {title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_filter: true, orderable: false, render: (data, type, full, meta) => { return full.fields.lot.pays_origine ? full.fields.lot.pays_origine.code_pays : '' }},
'eec': {title:'EEC', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.eec }, tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
'el': {title:'EL', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.el }, tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
'ep': {title:'EP', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.ep }, tooltip: 'Émissions résultant de la transformation'},
'etd': {title:'ETD', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.etd }, tooltip: 'Émissions résultant du transport et de la distribution'},
'eu': {title:'EU', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.eu }, tooltip: 'Émissions résultant du carburant à l\'usage'},
'esca': {title:'ESCA', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.esca }, tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
'eccs': {title:'ECCS', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.eccs }, tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
'eccr': {title:'ECCR', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.eccr }, tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
'eee': {title:'EEE', hidden: true, can_hide: true, render: (data, type, full, meta) => { return full.fields.lot.eee }, tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
'ghg_total': {title:'E', can_hide: true, is_read_only: true, render: (data, type, full, meta) => { return full.fields.lot.ghg_total }, tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
'ghg_reference': {title:'Émissions de référence', hidden: true, can_hide: true, is_read_only: true, render: (data, type, full, meta) => { return full.fields.lot.ghg_reference }, tooltip: 'Total des émissions du carburant fossile de référence'},
'ghg_reduction': {title:'% de réduction', can_hide: true, is_read_only: true, render: (data, type, full, meta) => { return full.fields.lot.ghg_reduction }},
'dae': {title:'N°Document douanier', can_hide: true, render: (data, type, full, meta) => {return full.fields.dae}},
'vendor': {title:'Fournisseur', can_hide: true, render: (data, type, full, meta) => {return full.fields.carbure_vendor ? full.fields.carbure_vendor.name : full.fields.unknown_vendor }},
'champ_libre': {title:'Champ libre', can_hide: true, can_filter: true, orderable: false, tooltip: 'Champ libre - Référence client', render: (data, type, full, meta) => {return full.fields.champ_libre}},
'delivery_date': {title:'Date de livraison', can_hide: true, render: (data, type, full, meta) => {return full.fields.delivery_date}},
'delivery_status': {title:'Statut', can_hide: true, render: (data, type, full, meta) => {return full.fields.delivery_status}},
'client': {title:'Client', can_hide: true, can_filter: true, orderable: false, render: (data, type, full, meta) => {return full.fields.carbure_client ? full.fields.carbure_client.name : full.fields.unknown_client}},
'delivery_site': {title:'Site de livraison', can_hide: true, can_filter: true, orderable: false, render: (data, type, full, meta) => {return full.fields.carbure_delivery_site ? full.fields.carbure_delivery_site.name : full.fields.unknown_delivery_site }},
'depot': {title:'Dépôt', can_hide: true, can_filter: true, orderable: true, render: (data, type, full, meta) => {return full.fields.carbure_delivery_site ? full.fields.carbure_delivery_site.name : full.fields.unknown_delivery_site }},
}

const producer_columns_drafts = ['checkbox', 'id', 'producer', 'production_site', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date', 'client', 'delivery_site']

const producer_columns_corrections = ['delivery_status', 'period', 'carbure_id', 'client', 'delivery_site', 'producer', 'production_site', 'production_country', 'volume', 'biocarburant', 'matiere_premiere',
'pays_origine', 'ghg_total', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date']

const producer_columns_in = ['checkbox', 'id', 'delivery_status', 'carbure_id', 'producer', 'production_site', 'production_country', 'vendor', 'biocarburant', 'matiere_premiere', 'volume', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date',  'delivery_site']

const producer_columns_mb_drafts = ['checkbox', 'lot_source', 'producer', 'production_site', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine', 'client', 'delivery_site',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date']

const producer_columns_mb = ['checkbox', 'carbure_id', 'depot', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine', 'producer', 'production_site',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre']

const producer_columns_out = ['carbure_id', 'producer', 'production_site', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date', 'client', 'delivery_site']



const operators_columns_drafts = ['checkbox', 'id', 'producer', 'production_site', 'ps_com_date', 'ps_ref', 'ps_dbl', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date', 'delivery_site']

const operators_columns_in = ['checkbox', 'id', 'delivery_status', 'carbure_id', 'producer', 'production_site', 'production_country', 'vendor', 'biocarburant', 'matiere_premiere', 'volume', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date',  'delivery_site']

const operators_columns_out = ['carbure_id', 'producer', 'production_site', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date', 'delivery_site']


const traders_columns_drafts = ['checkbox', 'id', 'producer', 'production_site', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date', 'client', 'delivery_site']

var administrators_columns =['carbure_id', 'producer', 'production_site', 'volume', 'biocarburant', 'matiere_premiere', 'pays_origine',
'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'dae', 'champ_libre', 'delivery_date', 'client', 'delivery_site']


/* modals management */
var modals = document.getElementsByClassName("modal__backdrop");

for (let i = 0, len = modals.length; i < len; i++) {
  let modalid = modals[i].id
  let modal = document.getElementById(modalid)
  let btn_open_id = "btn_open_" + modalid
  var btn_open_modal = document.getElementById(btn_open_id)

  if (btn_open_modal !== null) {
    btn_open_modal.onclick = function() {
      modal.style.display = "flex"
      window.modal = modal
    }
  }
}

var btns_close = document.getElementsByClassName("close")
for (let i = 0, len = btns_close.length; i < len; i++) {
  let btnid = btns_close[i].id
  let btn = document.getElementById(btnid)
  btn.onclick = function() {
    // close modal
    window.modal.style.display = "none"
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
    window.modal = modal
    window.modal.style.display = "flex"
    $("#modal_site_edit_site").val(site_id)
  }
}

var btns_delete_certif = document.getElementsByClassName("btn_open_modal_delete_certif")
for (let i = 0, len = btns_delete_certif.length; i < len; i++) {
  let btn = btns_delete_certif[i]
  let crtid = btn.dataset.crtid
  btn.onclick = function() {
    let modal = document.getElementById("modal_certif_delete")
    window.modal = modal
    window.modal.style.display = "flex"
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
    url         : window.api_lot_duplicate_v2,
    data        : formdata,
    type        : 'POST',
    processData : false,
    contentType : false,
    success     : function(data, textStatus, jqXHR){
      // Callback code
      window.table.ajax.reload()
      selected_drafts.pop()
      manage_actions_producers_drafts()
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
  if (selected_drafts.length > 0) {
    $("#btn_open_modal_validate_lots").addClass('primary')
    $("#btn_open_modal_validate_lots").css("pointer-events", "auto")
    $("#btn_open_modal_validate_lots").removeClass('secondary')
    // add drafts to validate modal
    $("#modal_validate_lots_list").empty()
    let to_validate = []
    for (let i = 0, len = selected_drafts.length; i < len; i++) {
      let rowdata = window.table.row(selected_drafts[i]).data()
      let lot = rowdata.fields.lot
      $("#modal_validate_lots_list").append(`<li>${lot.carbure_producer ? lot.carbure_producer.name : lot.unknown_producer} - ${lot.volume} - ${lot.biocarburant ? lot.biocarburant.name : ""} - ${lot.matiere_premiere ? lot.matiere_premiere.name : ""}</li>`)
      to_validate.push(rowdata.pk)
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

function manage_validate_button_mb_drafts() {
  if (selected_mb_drafts.length > 0) {
    $("#btn_open_modal_validate_lots").addClass('primary')
    $("#btn_open_modal_validate_lots").css("pointer-events", "auto")
    $("#btn_open_modal_validate_lots").removeClass('secondary')
    $("#modal_validate_lots_list").empty()
    let to_validate = []
    for (let i = 0, len = selected_mb_drafts.length; i < len; i++) {
      let rowdata = window.table.row(selected_mb_drafts[i]).data()
      $("#modal_validate_lots_list").append(`<li>${rowdata.fields.lot.volume} - ${rowdata.fields.lot.biocarburant.name} - ${rowdata.fields.lot.matiere_premiere.name}</li>`)
      to_validate.push(rowdata.pk)
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


function manage_delete_button_mb_drafts() {
  if (selected_mb_drafts.length > 0) {
    $("#btn_open_modal_delete_lots").addClass('primary')
    $("#btn_open_modal_delete_lots").css("pointer-events", "auto")
    $("#btn_open_modal_delete_lots").removeClass('secondary')
    $("#modal_delete_lots_list").empty()
    let to_delete = []
    for (let i = 0, len = selected_mb_drafts.length; i < len; i++) {
      let rowdata = window.table.row(selected_mb_drafts[i]).data()
      $("#modal_delete_lots_list").append(`<li>${rowdata.fields.lot.volume} - ${rowdata.fields.lot.biocarburant ? rowdata.fields.lot.biocarburant.name : ''} - ${rowdata.fields.lot.matiere_premiere ? rowdata.fields.lot.matiere_premiere.name : ''}</li>`)
      to_delete.push(rowdata.fields.lot.id)
      $("#modal_delete_lots_lots").val(to_delete.join(","))
    }
  } else {
    $("#btn_open_modal_delete_lots").addClass('secondary')
    $("#btn_open_modal_delete_lots").removeClass('primary')
    $("#btn_open_modal_delete_lots").css("pointer-events", "none")
    $("#modal_delete_lots_list").empty()
  }
}


function manage_delete_button() {
  if (selected_drafts.length > 0) {
    $("#btn_open_modal_delete_lots").addClass('primary')
    $("#btn_open_modal_delete_lots").css("pointer-events", "auto")
    $("#btn_open_modal_delete_lots").removeClass('secondary')
    $("#modal_delete_lots_list").empty()
    let to_delete = []
    for (let i = 0, len = selected_drafts.length; i < len; i++) {
      let rowdata = window.table.row(selected_drafts[i]).data()
      let lot = rowdata.fields.lot
      $("#modal_delete_lots_list").append(`<li>${lot.carbure_producer ? lot.carbure_producer.name : lot.unknown_producer} - ${lot.volume} - ${lot.biocarburant ? lot.biocarburant.name : ""} - ${lot.matiere_premiere ? lot.matiere_premiere.name : ""}</li>`)
      to_delete.push(rowdata.pk)
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
  if (selected_drafts.length === 1) {
    let tx_id = window.table.row(selected_drafts[0]).data().pk
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
    url         : window.api_production_sites_autocomplete + `?producer_id=${window.producer_id}&query=`,
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
    url         : window.api_mps_autocomplete + `?producer_id=${window.producer_id}&query=`,
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
    url         : window.api_biocarburants_autocomplete + `?producer_id=${window.producer_id}&query=`,
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

function manage_actions_producers_drafts() {
  // buttons Valider, Supprimer et Ajouter
  manage_validate_button()
  manage_delete_button()
  manage_duplicate_button()
}


function manage_actions() {
  console.log('manage_actions - deprecated')
  // buttons Valider, Supprimer et Ajouter
  manage_validate_button()
  manage_delete_button()
  manage_duplicate_button()
}

function manage_actions_mb() {
  // bouton Fusionner
  manage_fuse_button_mb()
}

function manage_actions_mb_drafts() {
  // buttons Valider et Supprimer
  manage_validate_button_mb_drafts()
  manage_delete_button_mb_drafts()
}

function manage_fuse_button_mb() {
  if (selected_mb.length > 1) {
    $("#btn_open_modal_fuse_lots").addClass('primary')
    $("#btn_open_modal_fuse_lots").css("pointer-events", "auto")
    $("#btn_open_modal_fuse_lots").removeClass('secondary')
    $("#modal_fuse_lots_list").empty()
    let to_fuse = []
    for (let i = 0, len = selected_mb.length; i < len; i++) {
      let rowdata = window.table.row(selected_mb[i]).data()
      let lot = rowdata.fields.lot
      to_fuse.push(rowdata.pk)
      $("#modal_fuse_lots_list").append(`<li>${lot.carbure_producer ? lot.carbure_producer.name : lot.unknown_producer} - ${lot.volume} - ${lot.biocarburant.name} - ${lot.matiere_premiere.name}</li>`)
      $("#modal_fuse_lots_txids").val(to_fuse.join(","))
    }
  } else {
    $("#btn_open_modal_fuse_lots").addClass('secondary')
    $("#btn_open_modal_fuse_lots").css("pointer-events", "none")
    $("#btn_open_modal_fuse_lots").removeClass('primary')
    // cleanup validate modal
    $("#modal_fuse_lots_list").empty()
  }
}


function manage_accept_button() {
  if (selected_in.length > 0) {
    $("#btn_open_modal_accept_lots").addClass('primary')
    $("#btn_open_modal_accept_lots").css("pointer-events", "auto")
    $("#btn_open_modal_accept_lots").removeClass('secondary')
    $("#modal_accept_lots_list").empty()
    let to_accept = []
    for (let i = 0, len = selected_in.length; i < len; i++) {
      let rowdata = window.table.row(selected_in[i]).data()
      let lot = rowdata.fields.lot
      to_accept.push(rowdata.pk)
      $("#modal_accept_lots_list").append(`<li>${lot.producer_is_in_carbure ? lot.carbure_producer.name : lot.unknown_producer} - ${lot.volume} - ${lot.biocarburant.name} - ${lot.matiere_premiere.name}</li>`)
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


function manage_actions_in() {
  // bouton Accepter Lots
  manage_accept_button()
}


function manage_actions_operators_drafts() {
  // boutons Dupliquer / Supprimer Lots
  manage_delete_button()
  manage_duplicate_button()
  manage_validate_button()
}

function manage_actions_operators_in() {
  // bouton Accepter Lots
  manage_accept_button()
}


function initFilters(table, dom) {
  console.log(`initFilters ${dom}`)
  var table_columns_filter = $(`#table_columns_${dom}_filter`)
  var table_columns_filter2 = $(`#table_columns_${dom}_filter2`)
  var columns_filter_html = ""
  var columns_filter_html2 = ""
  for (let i = 0, len = table.length; i < len; i++) {
    let column_name = table[i]
    let column = columns_definitions[column_name]
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

function display_lot_modal(table, columns, event, display_type) {
  // check if we clicked on the checkbox
  let colid = event.target._DT_CellIndex.column
  let rowid = event.target._DT_CellIndex.row
  let data = table.row(rowid).data()
  let column_name = columns[colid]
  let column_definition = columns_definitions[column_name]
  let comments_section = $("#comments_list")
  comments_section.empty()
  $("#btn_close_modal_lot_save").on('click', function() {
    window.modal = document.getElementById('modal_lot')
    window.modal.style.display = 'none';
  })

  if (column_name['data'] === 'checkbox') {
    // ignore clicks on checkbox column
    return
  } else {
    window.modal = document.getElementById("modal_lot")
    let lot = data.fields.lot
    let tx = data.fields

    console.log(`display lot modal`)
    console.log(data)
    $("#save_section").hide()
    $("#check_section").hide()
    $("#correct_section").hide()
    if (display_type === 'draft') {
      $("#save_section").show()
    } else if (display_type === 'in') {
      $("#check_section").show()
    } else if (display_type === 'correction') {
      $("#correct_section").show()
    } else if (display_type === 'mb') {
      // read only
    } else {
      console.log(`unknown display_type ${display_type}`)
      return
    }

    $("#lot_id").val(lot.id)
    $("#tx_id").val(data.pk)

    if (lot.producer_is_in_carbure) {
      producer_is_in_carbure(true)
    } else {
      producer_is_in_carbure(false)
    }

    $("#carbure_producer_name").val(lot.carbure_producer ? lot.carbure_producer.name : '')
    $("#carbure_producer_id").val(lot.carbure_producer ? lot.carbure_producer.id : '')
    if (data.errors['producer']) {
      $("#carbure_producer_name_error").val(data.errors['producer'])
    }
    $("#carbure_production_site_name").val(lot.carbure_production_site ? lot.carbure_production_site.name : '')
    $("#carbure_production_site_id").val(lot.carbure_production_site ? lot.carbure_production_site.id : '')
    if (data.errors['production_site']) {
      $("#carbure_production_site_name_error").val(data.errors['production_site'])
    }
    $("#unknown_producer_name").val(lot.unknown_producer)
    $("#unknown_production_site_name").val(lot.unknown_production_site)
    $("#unknown_production_site_country").val(lot.unknown_production_country ? lot.unknown_production_country.name : '')
    $("#unknown_production_site_country_code").val(lot.unknown_production_country ? lot.unknown_production_country.code_pays : '')

    $("#unknown_production_site_com_date").val(lot.unknown_production_site_com_date)
    $("#unknown_production_site_reference").val(lot.unknown_production_site_reference)
    $("#unknown_production_site_dbl_counting").val(lot.unknown_production_site_dbl_counting)



    $("#volume").val(lot.volume)
    if (data.errors['volume']) {
      $("#volume_error").val(data.errors.volume)
    }
    $("#biocarburant").val(lot.biocarburant ? lot.biocarburant.name : '')
    $("#biocarburant_code").val(lot.biocarburant ? lot.biocarburant.code : '')
    if (data.errors['biocarburant']) {
      $("#biocarburant_error").val(data.errors.biocarburant)
    }
    $("#matiere_premiere").val(lot.matiere_premiere ? lot.matiere_premiere.name : '')
    $("#matiere_premiere_code").val(lot.matiere_premiere ? lot.matiere_premiere.code : '')
    if (data.errors['matiere_premiere']) {
      $("#matiere_premiere_error").val(data.errors.matiere_premiere)
    }
    $("#pays_origine").val(lot.pays_origine ? lot.pays_origine.name : '')
    $("#pays_origine_code").val(lot.pays_origine ? lot.pays_origine.code_pays : '')
    if (data.errors['pays_origine']) {
      $("#pays_origine_error").val(data.errors.pays_origine)
    }
    /* TX Related fields */
    $("#dae").val(tx.dae)
    if (data.errors['dae']) {
      $("#dae_error").val(data.errors.dae)
    }

    if (tx.client_is_in_carbure) {
      client_is_in_carbure(true)
    } else {
      client_is_in_carbure(false)
    }
    if (tx.delivery_site_is_in_carbure) {
      delivery_site_is_in_carbure(true)
    } else {
      delivery_site_is_in_carbure(false)
    }

    $("#carbure_client").val(tx.carbure_client ? tx.carbure_client.name : '')
    $("#carbure_client_id").val(tx.carbure_client ? tx.carbure_client.id : '')
    if (data.errors['client']) {
      $("#carbure_client_error").val(data.errors.client)
    }
    $("#carbure_delivery_site").val(tx.carbure_delivery_site ? tx.carbure_delivery_site.name : '')
    $("#carbure_delivery_site_id").val(tx.carbure_delivery_site ? tx.carbure_delivery_site.depot_id : '')
    if (data.errors['delivery_site']) {
      $("#carbure_delivery_site_error").val(data.errors.delivery_site)
    }
    $("#unknown_client").val(tx.unknown_client)
    $("#unknown_delivery_site").val(tx.unknown_delivery_site)
    $("#unknown_delivery_site_country").val(tx.unknown_delivery_site_country ? tx.unknown_delivery_site_country.name : '')
    $("#unknown_delivery_site_country_code").val(tx.unknown_delivery_site_country ? tx.unknown_delivery_site_country.code_pays : '')
    $("#delivery_date").val(tx.delivery_date)
    if (data.errors['delivery_date']) {
      $("#delivery_date_error").val(data.errors.delivery_date)
    }
    $("#champ_libre").val(tx.champ_libre)

    /* Greenhouse gases values */
    $("#eec").val(lot.eec)
    $("#el").val(lot.el)
    $("#ep").val(lot.ep)
    $("#etd").val(lot.etd)
    $("#eu").val(lot.eu)
    $("#esca").val(lot.esca)
    $("#eccs").val(lot.eccs)
    $("#eccr").val(lot.eccr)
    $("#eee").val(lot.eee)

    // non-input keys
    $("#ghg_total").html(lot.ghg_total)
    $("#ghg_reduction").html(`${lot.ghg_reduction}%`)
    $("#ghg_reference").val(lot.ghg_reference)
    $("#reduction_title").attr('title', `Par rapport à des émissions fossiles de référence de ${lot.ghg_reference} gCO2eq/MJ`)

    if (data.comments.length) {
      for (let i = 0, len = data.comments.length; i < len; i++) {
        let c = data.comments[i]
        // console.log(c)
        let html = `<dd><b>${c.fields.entity.name}</b>: ${c.fields.comment}</dd>`
        comments_section.append(html)
      }
    }
    window.modal.style.display = "flex"
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
    url         : window.api_lot_save_v2,
    data        : formdata,
    cache       : false,
    contentType : false,
    processData : false,
    type        : 'POST',
    success     : function(data, textStatus, jqXHR) {
      // Callback code
      // if there's an additional comment, save it as well
      let comment = $("#new_comment").val()
      if (comment) {
        var formcomment = new FormData();
        formcomment.set('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value)
        formcomment.set('lot_id', document.getElementById('lot_id').value)
        formcomment.set('tx_id', document.getElementById('tx_id').value)
        formcomment.set('comment', comment)
        $.ajax({
          url         : window.api_lot_add_comment_v2,
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
    url         : window.api_ges + `?mp=${mp}&bc=${bc}`,
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
  serviceUrl: window.api_mps_autocomplete,
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
  serviceUrl: window.api_biocarburants_autocomplete,
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
  serviceUrl: window.api_producers_autocomplete_v2,
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
  serviceUrl: window.api_production_sites_autocomplete,
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
  serviceUrl: window.api_clients_autocomplete_v2,
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
  serviceUrl: window.api_depots_autocomplete_v2,
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

function handleTableEvents(table, tbl_id, cb, selection_array) {
  // search box
  $('#input_search_datatable').on('keyup', function() {
      table.search(this.value).draw()
  })

  // Handle click on checkbox
  $(`#${tbl_id} tbody`).on('click', 'input[type="checkbox"]', function(e) {
    var $row = $(this).closest('tr')
    // Get row data
    var rowId = table.row($row).index()
    // Determine whether row ID is in the list of selected row IDs
    var index = $.inArray(rowId, selection_array)
    // If checkbox is checked and row ID is not in list of selected row IDs
    if(this.checked && index === -1) {
      selection_array.push(rowId)
    // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
    } else if (!this.checked && index !== -1) {
      selection_array.splice(index, 1)
    }
    // Update state of "Select all" control
    updateDataTableSelectAllCtrl(table);
    // Prevent click event from propagating to parent
    e.stopPropagation()
    // Show/Hide buttons depending on selected_rows content
    cb()
  })

  // Handle click on "Select all" control
  $('thead input[name="select_all"]', table.table().container()).on('click', function(e) {
  	console.log(`clicked select all`)
    if (this.checked) {
       $(`#${tbl_id} tbody input[type="checkbox"]:not(:checked)`).trigger('click')
    } else {
       $(`#${tbl_id} tbody input[type="checkbox"]:checked`).trigger('click')
    }
    // Prevent click event from propagating to parent
    e.stopPropagation()
  })

  // Handle table draw event
  table.on('draw', function() {
    // Update state of "Select all" control
    updateDataTableSelectAllCtrl(table)
  })
}

function parseApiFetchResponse(res) {
    data = {}
    txs = JSON.parse(res['transactions'])
    for (let i = 0, len = txs.length; i < len; i++) {
      let tx = txs[i]
      data[tx.pk] = tx
      data[tx.pk].errors = {}
      data[tx.pk].comments = []
    }
    if (res.comments !== undefined) {
      comments = JSON.parse(res['comments'])
      for (let i = 0, len = comments.length; i < len; i++) {
        let comment = comments[i]
        let txid = comment.fields.tx
        if (data[txid] !== undefined) {
          data[txid].comments.push(comment)
        } else {
          console.log(`Error. got comment on txid ${txid} but did not get associated tx.`)
          console.log(data)
        }
      }
    }
    list = Object.values(data)
    return list
}


const dt_producers_drafts_columns = []
for (let i = 0, len = producer_columns_drafts.length; i < len; i++) {
  let colname = producer_columns_drafts[i]
  dt_producers_drafts_columns.push(columns_definitions[colname])
}

const dt_producers_drafts_config = {
  is_complex_dt: true,
  id: "datatable_drafts",
  url: window.api_get_drafts,
  col_definition: dt_producers_drafts_columns,
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
        let col_name = producer_columns_drafts[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, producer_columns_drafts, e, 'draft')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(producer_columns_drafts, "tab_drafts")
    handleTableEvents(table, tbl_id, manage_actions_producers_drafts, selected_drafts)
    manage_actions_producers_drafts()
  }
}


const dt_producers_corrections_columns = []
for (let i = 0, len = producer_columns_corrections.length; i < len; i++) {
  let colname = producer_columns_corrections[i]
  dt_producers_corrections_columns.push(columns_definitions[colname])
}


const dt_producers_corrections_config = {
  is_complex_dt: true,
  id: "datatable_corrections",
  url: window.api_get_corrections,
  col_definition: dt_producers_corrections_columns,
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
        let col_name = producer_columns_corrections[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, producer_columns_corrections, e, 'correction')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(producer_columns_corrections, "tab_corrections")
  }
}

const dt_producers_in_columns = []
for (let i = 0, len = producer_columns_in.length; i < len; i++) {
  let colname = producer_columns_in[i]
  dt_producers_in_columns.push(columns_definitions[colname])
}

const dt_producers_in_config = {
  is_complex_dt: true,
  id: "datatable_in",
  url: window.api_get_in,
  col_definition: dt_producers_in_columns,
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
        let col_name = producer_columns_in[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, producer_columns_in, e, 'in')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(producer_columns_in, "tab_in")
    handleTableEvents(table, tbl_id, manage_actions_in, selected_in)
    manage_actions_in()
  }
}

const dt_producers_mb_columns = []
for (let i = 0, len = producer_columns_mb.length; i < len; i++) {
  let colname = producer_columns_mb[i]
  dt_producers_mb_columns.push(columns_definitions[colname])
}

const dt_producers_mb_config = {
  is_complex_dt: true,
  id: "datatable_mb",
  url: window.api_get_mb,
  col_definition: dt_producers_mb_columns,
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
        let col_name = producer_columns_mb[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, producer_columns_mb, e, 'mb')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(producer_columns_mb, "tab_mb")
    handleTableEvents(table, tbl_id, manage_actions_mb, selected_mb)
    manage_actions_mb()
  }
}

const dt_producers_mb_drafts_columns = []
for (let i = 0, len = producer_columns_mb_drafts.length; i < len; i++) {
  let colname = producer_columns_mb_drafts[i]
  dt_producers_mb_drafts_columns.push(columns_definitions[colname])
}

const dt_producers_mb_drafts_config = {
  is_complex_dt: true,
  id: "datatable_mb_drafts",
  url: window.api_get_mb_drafts,
  col_definition: dt_producers_mb_drafts_columns,
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
        let col_name = producer_columns_mb_drafts[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, producer_columns_mb_drafts, e, 'mb')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(producer_columns_mb_drafts, "tab_mb_drafts")
    handleTableEvents(table, tbl_id, manage_actions_mb_drafts, selected_mb_drafts)
    manage_actions_mb_drafts()
  }
}


const dt_producers_out_columns = []
for (let i = 0, len = producer_columns_out.length; i < len; i++) {
  let colname = producer_columns_out[i]
  dt_producers_out_columns.push(columns_definitions[colname])
}

const dt_producers_out_config = {
  is_complex_dt: true,
  id: "datatable_out",
  url: window.api_get_out,
  col_definition: dt_producers_out_columns,
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
        let col_name = producer_columns_out[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, producer_columns_out, e, 'mb')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(producer_columns_out, "tab_out")
  }
}








const dt_operators_drafts_columns = []
for (let i = 0, len = operators_columns_drafts.length; i < len; i++) {
  let colname = operators_columns_drafts[i]
  dt_operators_drafts_columns.push(columns_definitions[colname])
}

const dt_operators_drafts_config = {
  is_complex_dt: true,
  id: "datatable_drafts",
  url: window.api_get_drafts,
  col_definition: dt_operators_drafts_columns,
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
        let col_name = operators_columns_drafts[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, operators_columns_drafts, e, 'draft')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(operators_columns_drafts, "tab_operators_drafts")
    handleTableEvents(table, tbl_id, manage_actions_operators_drafts, selected_drafts)
    manage_actions_operators_drafts()
  }
}


const dt_operators_in_columns = []
for (let i = 0, len = operators_columns_in.length; i < len; i++) {
  let colname = operators_columns_in[i]
  dt_operators_in_columns.push(columns_definitions[colname])
}

const dt_operators_in_config = {
  is_complex_dt: true,
  id: "datatable_in",
  url: window.api_get_in,
  col_definition: dt_operators_in_columns,
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
        let col_name = operators_columns_in[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, operators_columns_in, e, 'in')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(operators_columns_in, "tab_operators_in")
    handleTableEvents(table, tbl_id, manage_actions_operators_in, selected_in)
    manage_actions_operators_in()
  }
}


const dt_operators_out_columns = []
for (let i = 0, len = operators_columns_out.length; i < len; i++) {
  let colname = operators_columns_out[i]
  dt_operators_out_columns.push(columns_definitions[colname])
}

const dt_operators_out_config = {
  is_complex_dt: true,
  id: "datatable_out",
  url: window.api_get_out,
  col_definition: dt_operators_out_columns,
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
        let col_name = operators_columns_out[meta.col]
        let cd = columns_definitions[col_name]
        return cd['render'](full)
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, operators_columns_out, e, 'mb')
    })
    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw();
    })
    initFilters(operators_columns_out, "tab_operators_out")
  }
}


const dt_admin_users = {
  id: "datatable_users",
  dt_config: {
    paging: false,
  },
}

const dt_admin_entities = {
  id: "datatable_entities",
  dt_config: {
    paging: false,
  },
}

const dt_admin_rights = {
  id: "datatable_rights",
  dt_config: {
    paging: false,
  },
}

const dt_admin_columns = []
for (let i = 0, len = administrators_columns.length; i < len; i++) {
  let colname = administrators_columns[i]
  dt_admin_columns.push(columns_definitions[colname])
}

const dt_admin_lots = {
  is_complex_dt: true,
  id: "datatable",
  url: window.api_get_out,
  col_definition: dt_admin_columns,
  paging: true,
  info: true,
  dom: 'rtp',
  serverSide: true,
  processing: true,
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
        let col_name = administrators_columns[meta.col].data
        if (administrators_columns[meta.col]['render'] != undefined) {
          return administrators_columns[meta.col]['render'](full)
        }
        return full['fields'][col_name]
      }
    },
  ],
  order: [[ 1, 'desc' ]],
  ajax_dataSrc: parseApiFetchResponse,
  post_init: function(table) {
    let tbl_id = table.table().node().id
    $(`#${tbl_id} tbody`).on('click', 'td',  (e) => {
      display_lot_modal(table, administrators_columns, e, 'mb')
    })

    $('#input_search_datatable').on('keyup', function() {
        table.search(this.value).draw()
    })

    initFilters(administrators_columns, "admin_tab_out")
  }
}

// producer
dt_config['tab_drafts'] = dt_producers_drafts_config
dt_config['tab_corrections'] = dt_producers_corrections_config
dt_config['tab_in'] = dt_producers_in_config
dt_config['tab_mb'] = dt_producers_mb_config
dt_config['tab_mb_drafts'] = dt_producers_mb_drafts_config
dt_config['tab_out'] = dt_producers_out_config

// operators
dt_config['tab_operators_drafts'] = dt_operators_drafts_config
dt_config['tab_operators_in'] = dt_operators_in_config
dt_config['tab_operators_out'] = dt_operators_out_config

// admin tabs
dt_config['tab_users'] = dt_admin_users
dt_config['tab_entities'] = dt_admin_entities
dt_config['tab_rights'] = dt_admin_rights
dt_config['admin_tab_out'] = dt_admin_lots


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

  init_tab_generic(this.dataset.dst)
})

$("#btn_add_tx_comment").on('click', handleSave)

$("#btn_accept_lot").on('click', function() {
  let tx_id = $("#tx_id").val()
  $.ajax({
    url: window.api_lot_accept_v2,
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
    url: window.api_lot_reject_v2,
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
    url: window.api_lot_accept_with_correction_v2,
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

function init_tab_generic(tab_name) {
  const config = dt_config[tab_name]
  const tblselector = `#${config.id}`
  if (!$.fn.DataTable.isDataTable(tblselector)) {
    if (config.is_complex_dt) {
      var table = $(tblselector).DataTable({
        paging: config.paging,
        info: config.info,
        dom: config.dom,
        scrollX: true,
        columnDefs: config.columnDefs,
        order: config.order,
        columns: config.col_definition,
        processing: config.processing,
        serverSide: config.serverSide,
        ajax: {
          url: config.url,
          dataSrc: config.ajax_dataSrc,
        },
        initComplete: config.initComplete,
      })
      if (config.post_init) {
        config.post_init(table)
      }
      var tablesettings = loadTableSettings(config.col_definition, tab_name)
      showHideTableColumns(table, tablesettings, tab_name)
    } else {
      var table = $(tblselector).DataTable(config.dt_config)
    }
    window[config.id] = table
    window.table = table
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



