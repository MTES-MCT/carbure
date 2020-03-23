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

$(document).ready(function() {
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




