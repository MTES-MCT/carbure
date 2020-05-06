/* modals management */
var table_columns_drafts = [
{title:'<input type="checkbox" id="checkbox_header"/>', can_hide: false, can_duplicate: false, can_export: false, read_only: true, data:'checkbox'},
{title:'Producteur', can_hide: true, can_duplicate: true, can_export: true, data:'producer_name'},
{title:'Site de<br /> Production', filter_title: 'Site', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Volume<br /> à 20°C<br /> en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', filter_title:'MP', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, filter_title: 'Pays', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br /> en EA', can_hide: true, can_duplicate: true, can_export: true, data:'ea_delivery_date'},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_name'},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
]

var table_columns_producers_corrections = [
{title:'Numéro de lot', can_hide: true, can_duplicate: false, can_export: true, data:'carbure_id'},
{title:'Producteur', can_hide: true, can_duplicate: true, can_export: true, data:'producer_name'},
{title:'Site de<br />Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Volume<br /> à 20°C<br />en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br />en EA', can_hide: true, can_duplicate: true, can_export: true, data:'ea_delivery_date'},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_name'},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
{title:'Statut', can_hide: true, can_duplicate: false, read_only: true, can_filter: true, orderable: false, can_export: false, data: 'ea_delivery_status'},
{title:`<input type="checkbox" id="checkbox_header"/>`, can_hide: false, can_duplicate: false, read_only: true, can_export: false, data:'checkbox'},
]

var table_columns_operators = [
{title:'Fournisseur', can_hide: true, can_duplicate: true, can_export: true, data:'producer_name'},
{title:'Site de<br />Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Numéro de lot', can_hide: true, can_duplicate: false, can_export: true, data:'carbure_id'},
{title:'Volume<br /> à 20°C<br />en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br />en EA', can_hide: true, can_duplicate: true, can_export: true, data:'ea_delivery_date'},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
{title:'Statut', can_hide: true, can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_status'},
{title:`<input type="checkbox" id="checkbox_header"/>`, can_hide: false, can_duplicate: false, read_only: true, can_export: false, data:'checkbox'},
]

var table_columns_administrators = [
{title:'Producteur', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'producer_name'},
{title:'Site de<br />Production', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'production_site_name'},
{title:'Numéro de lot', can_hide: true, can_duplicate: false, can_export: true, data:'carbure_id'},
{title:'Volume<br /> à 20°C<br />en Litres', can_hide: true, can_duplicate: true, can_export: true, data: 'volume'},
{title:'Biocarburant', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'biocarburant_name'},
{title:'Matière<br /> Première', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'matiere_premiere_name'},
{title:`Pays<br /> d'origine`, can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'pays_origine_name'},

{title:'EEC', can_hide: true, can_duplicate: true, can_export: true, data: 'eec', tooltip: 'Émissions résultant de l\'extraction ou de la culture des matières premières'},
{title:'EL', can_hide: true, can_duplicate: true, can_export: true, data: 'el', tooltip: 'Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l\'affectation des sols'},
{title:'EP', can_hide: true, can_duplicate: true, can_export: true, data: 'ep', tooltip: 'Émissions résultant de la transformation'},
{title:'ETD', can_hide: true, can_duplicate: true, can_export: true, data: 'etd', tooltip: 'Émissions résultant du transport et de la distribution'},
{title:'EU', can_hide: true, can_duplicate: true, can_export: true, data: 'eu', tooltip: 'Émissions résultant du carburant à l\'usage'},
{title:'ESCA', can_hide: true, can_duplicate: true, can_export: true, data: 'esca', tooltip: 'Réductions d\'émissions dues à l\'accumulation du carbone dans les sols grâce à une meilleure gestion agricole'},
{title:'ECCS', can_hide: true, can_duplicate: true, can_export: true, data: 'eccs', tooltip: 'Réductions d\'émissions dues au piégeage et au stockage géologique du carbone'},
{title:'ECCR', can_hide: true, can_duplicate: true, can_export: true, data: 'eccr', tooltip: 'Réductions d\'émissions dues au piégeage et à la substitution du carbone'},
{title:'EEE', can_hide: true, can_duplicate: true, can_export: true, data: 'eee', tooltip: 'Réductions d\'émissions dues à la production excédentaire d\'électricité dans le cadre de la cogénération'},
{title:'E', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_total', tooltip: 'Total des émissions résultant de l\'utilisation du carburant'},
{title:'Émissions de référence', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reference', tooltip: 'Total des émissions du carburant fossile de référence'},
{title:'% de réduction', can_hide: true, can_duplicate: true, is_read_only: true, can_export: true, data: 'ghg_reduction'},

{title:'N°DAE/DAU', can_hide: true, can_duplicate: false, can_export: true, data:'dae'},
{title:'Référence', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data:'client_id', tooltip: 'Champ libre - Référence client'},
{title:'Date d\'entrée<br />en EA', can_hide: true, can_duplicate: true, can_export: true, data:'ea_delivery_date'},
{title:'Client', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_name'},
{title:'Site de livraison', can_hide: true, can_duplicate: true, can_filter: true, orderable: false, can_export: true, data: 'ea_delivery_site'},
]


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

$(document).ready(function() {
  $(".tabs__tab").on('click', function(event) {
    // hide all tabs
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }

    // remove all tablinks class "selected"
    tablinks = document.getElementsByClassName("tabs__tab");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" tabs__tab--selected", "");
    }

    // add selected class to clicked tablink
    event.currentTarget.className += " tabs__tab--selected";
    // show destination
    document.getElementById(event.currentTarget.dataset.dst).style.display = "block";
  })


  $("form").submit(function(event) {
    let form = $(this);
    let form_id = form.attr('id')
    let form_url = form.attr('data-url')
    let err_msg_dom = $(`#${form_id}_err_message`)
    err_msg_dom.text("Envoi en cours, veuillez patienter...")
    var formdata = false;
    if (window.FormData){
      formdata = new FormData(form[0]);
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
        window.location.reload()
      },
      error       : function(e) {
        if (e.status === 400) {
          err_msg_dom.text(e.responseJSON.message)
          console.log(`server error ${JSON.stringify(e.responseJSON.extra)}`)
        } else {
          err_msg_dom.text("Server error. Please contact an administrator")
          console.log(`server error ${JSON.stringify(e)}`)
        }
      }
    });
    event.preventDefault()
  })
})

$("#pagelength").on('change', function() {
  let pagelength = $("#pagelength").val()
  table.page.len(pagelength).draw()
})

function loadTableSettings() {
  var tableSettings = localStorage.getItem('tableSettings');
  if (tableSettings === undefined || tableSettings === null) {
    let nb_columns = table.columns().data().length
    columns = Array(nb_columns).fill(1);
    saveTableSettings(columns)
  } else {
    columns = JSON.parse(tableSettings)
    let nb_columns = table.columns().data().length
    if (columns.length !== nb_columns) {
      columns = Array(nb_columns).fill(1);
      saveTableSettings(columns)
    }
  }
  return columns
}

function loadOperatorsTableSettings() {
  var tableSettings = localStorage.getItem('operatorsTableSettings');
  if (tableSettings === undefined || tableSettings === null) {
    let nb_columns = table.columns().data().length
    columns = Array(nb_columns).fill(1);
    saveOperatorsTableSettings(columns)
  } else {
    columns = JSON.parse(tableSettings)
    let nb_columns = table.columns().data().length
    if (columns.length !== nb_columns) {
      columns = Array(nb_columns).fill(1);
      saveOperatorsTableSettings(columns)
    }
  }
  return columns
}

function loadAdministratorsTableSettings() {
  var tableSettings = localStorage.getItem('administratorsTableSettings');
  if (tableSettings === undefined || tableSettings === null) {
    let nb_columns = table.columns().data().length
    columns = Array(nb_columns).fill(1);
    saveAdministratorsTableSettings(columns)
  } else {
    columns = JSON.parse(tableSettings)
    let nb_columns = table.columns().data().length
    if (columns.length !== nb_columns) {
      columns = Array(nb_columns).fill(1);
      saveAdministratorsTableSettings(columns)
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

function saveTableSettings(settings) {
  localStorage.setItem("tableSettings", JSON.stringify(settings));
}

function saveOperatorsTableSettings(settings) {
  localStorage.setItem("operatorsTableSettings", JSON.stringify(settings));
}

function saveAdministratorsTableSettings(settings) {
  localStorage.setItem("administratorsTableSettings", JSON.stringify(settings));
}

function saveAddLotSettings(settings) {
  localStorage.setItem("addLotSettings", JSON.stringify(settings));
}

function showHideTableColumns(columns) {
  /* display table columns depending on config */
  let nb_columns = table.columns().data().length

  for (let i = 0, len = nb_columns; i < len; i++) {
    let isChecked = columns[i]
    let boxid = '#checkbox' + i
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
  let nb_columns = table.columns().data().length
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
  // unselect
  for (const key in selected_rows) {
    delete selected_rows[key]
  }
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

  $.ajax({
    url         : "{% url 'producers-api-duplicate-lot' %}",
    data        : {'lot_id': lot_id, 'fields':fields_to_ignore, 'csrfmiddlewaretoken':document.getElementsByName('csrfmiddlewaretoken')[0].value},
    type        : 'POST',
    success     : function(data, textStatus, jqXHR){
      // Callback code
      window.table.ajax.reload()
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

function manage_validate_button(draft_present) {
 if (draft_present === true) {
    $("#btn_open_modal_validate_lots").addClass('primary')
    $("#btn_open_modal_validate_lots").css("pointer-events", "auto")
    $("#btn_open_modal_validate_lots").removeClass('secondary')
    // add drafts to validate modal
    $("#modal_validate_lots_list").empty()
    let to_validate = []
    let keys = Object.keys(selected_rows)
    for (let i = 0, len = keys.length; i < len; i++) {
      let key = keys[i]
      let rowdata = selected_rows[key]
      let statut = rowdata['status']
      if (statut.toLowerCase() === "draft") {
        $("#modal_validate_lots_list").append(`<li>${rowdata['production_site_name']} - ${rowdata['volume']} - ${rowdata['biocarburant_name']} - ${rowdata['matiere_premiere_name']}</li>`)
        to_validate.push(selected_rows[key]['lot_id'])
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

function manage_delete_button(only_drafts_present) {
  let keys = Object.keys(selected_rows)
  if (keys.length > 0 && only_drafts_present === true) {
    $("#btn_open_modal_delete_lots").addClass('primary')
    $("#btn_open_modal_delete_lots").css("pointer-events", "auto")
    $("#btn_open_modal_delete_lots").removeClass('secondary')
    $("#modal_delete_lots_list").empty()
    let to_delete = []
    let keys = Object.keys(selected_rows)
    for (let i = 0, len = keys.length; i < len; i++) {
      let key = keys[i]
      let rowdata = selected_rows[key]
      let statut = rowdata['status']
      if (statut.toLowerCase() === "draft") {
        $("#modal_delete_lots_list").append(`<li>${rowdata['production_site_name']} - ${rowdata['volume']} - ${rowdata['biocarburant_name']} - ${rowdata['matiere_premiere_name']}</li>`)
        to_delete.push(selected_rows[key]['lot_id'])
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

function manage_add_button() {
  let keys = Object.keys(selected_rows)
  if (keys.length === 1) {
    $("#add_lot").text("Dupliquer Lot")
    $("#add_lot").removeAttr("href")
    let lot_id = selected_rows[keys[0]]['lot_id']
    $("#add_lot").unbind('click')
    $("#add_lot").attr("onclick", `duplicate_lot(${lot_id})`)
  } else {
    $("#add_lot").text("Ajouter Lot")
    $("#add_lot").removeAttr("onclick")
    $("#add_lot").on("click", function() {
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
  }
}

function check_production_sites() {
  $.ajax({
    url         : "{% url 'producers-api-production-sites-autocomplete' %}" + "?producer_id={{user_entity.id}}&query=",
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
    url         : "{% url 'producers-api-mps-autocomplete' %}" + "?producer_id={{user_entity.id}}&query=",
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
    url         : "{% url 'producers-api-biocarburants-autocomplete' %}" + "?producer_id={{user_entity.id}}&query=",
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
  // if one of the rows is a draft, button Valider is active
  let draft_present = false
  let only_drafts_present = true
  let keys = Object.keys(selected_rows)
  for (let i = 0, len = keys.length; i < len; i++) {
    let key = keys[i]
    let rowdata = selected_rows[key]
    let statut = rowdata['status']
    if (statut.toLowerCase() === "draft") {
      draft_present = true
    } else {
      only_drafts_present = false
    }
  }
  manage_validate_button(draft_present)
  manage_delete_button(only_drafts_present)
  manage_add_button()
}

function initFilters(table) {
  var table_columns_filter = $("#table_columns_filter")
  var table_columns_filter2 = $("#table_columns_filter2")
  var list_columns_filter = $("#list_columns_filter")
  var columns_filter_html = ""
  var columns_filter_html2 = ""
  var list_columns_filter_html = ""
  for (let i = 0, len = table.length; i < len; i++) {
    let column = table[i]
    if (column.can_hide === true) {
      // use two columns
      if (i <= (len / 2)) {
        columns_filter_html += `<tr><td><input type="checkbox" id="checkbox${i}" class="toggle-vis" data-column="${i}"></td><td><label for="checkbox${i}" class="label-inline">${column.title}</label></td></tr>`
      } else {
        columns_filter_html2 += `<tr><td><input type="checkbox" id="checkbox${i}" class="toggle-vis" data-column="${i}"></td><td><label for="checkbox${i}" class="label-inline">${column.title}</label></td></tr>`
      }
    }
    if (column.can_duplicate === true) {
      list_columns_filter_html += `<li class="flex-item-a"><input type="checkbox" id="add_checkbox${i}" class="toggle-lot-param" data-column="${i}"><label for="add_checkbox${i}" class="label-inline">${column.title}</label></li>`
    }
  }
  table_columns_filter.append(columns_filter_html)
  table_columns_filter2.append(columns_filter_html2)
  list_columns_filter.append(list_columns_filter_html)
}