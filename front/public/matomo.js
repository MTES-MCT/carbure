var _paq = window._paq || []
;(function () {
  var u = "https://stats.data.gouv.fr/"
  _paq.push(["setTrackerUrl", u + "matomo.php"])
  _paq.push(["setSiteId", "134"])
  var d = document,
    g = d.createElement("script"),
    s = d.getElementsByTagName("script")[0]
  g.type = "text/javascript"
  g.async = true
  g.defer = true
  g.src = u + "matomo.js"
  s.parentNode.insertBefore(g, s)
})()
