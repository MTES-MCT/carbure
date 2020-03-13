// static data
var matieres_premieres = ["Betterave","Blé","Canne à sucre","Colza","Déchets organiques ménagers","Fumier humide","Fumier sec","Huiles ou graisses animales  (catégorie I et/ou II )","Huiles ou graisses animales  (catégorie III)","Huile de palme","Huile alimentaire usagée","Maïs","Résidus viniques","Soja ","Tournesol ","Glycérine brute","Déchets de bois","Déchets industriels","Algues","Paille","Boues d’épuration","Effluents d’huileries de palme et rafles","Brai de tallol.","Bagasse.","Coques","Balles (enveloppes).","Râpes","Déchets municipaux en mélange (Hors déchets ménagers triés)","Matières cellulosiques d’origine non alimentaire","Matières ligno-cellulosiques (Hors grumes de sciage & de placage)"]
var biocarburants = ["Biogaz","Biogazole de synthèse (Hors HVO)","EMHA","EMHU","EMHV","ETBE","Ethanol","HVO","MTBE","TAEE"]
var countries = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua &amp; Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia &amp; Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Cayman Islands","Central Arfrican Republic","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cuba","Curacao","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nauro","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","North Korea","Norway","Oman","Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre &amp; Miquelon","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","St Kitts &amp; Nevis","St Lucia","St Vincent","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad &amp; Tobago","Tunisia","Turkey","Turkmenistan","Turks &amp; Caicos","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States of America","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"];


/* modals management */
var modals = document.getElementsByClassName("modal__backdrop");

for (let i = 0, len = modals.length; i < len; i++) {
  let modalid = modals[i].id
  let modal = document.getElementById(modalid)
  let btn_open_modal = document.getElementById("btn_open_" + modalid)
  let btn_close_modal = document.getElementById("btn_close_" + modalid)
  if (btn_open_modal !== null) {
    btn_open_modal.onclick = function() {
      modal.style.display = "flex";
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

$(document).ready(function() {
  $("form").submit(function(event) {
    let form = $(this);
    let form_id = form.attr('id')
    console.log(`form submitted: ${form_id} err_msg id: #${form_id}_err_message`)
    let form_url = form.attr('data-url')
    let err_msg_dom = $(`#${form_id}_err_message`)
    err_msg_dom.text("Uploading... please wait")
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
      success     : function(data, textStatus, jqXHR){
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




