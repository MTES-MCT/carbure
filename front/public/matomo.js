var _paq = (window._paq = window._paq || [])
;(function () {
  var u = "https://stats.beta.gouv.fr/"
  _paq.push(["setTrackerUrl", u + "matomo.php"])
  _paq.push(["setSiteId", "60"])
  var d = document,
    g = d.createElement("script"),
    s = d.getElementsByTagName("script")[0]
  g.async = true
  g.src = u + "matomo.js"
  s.parentNode.insertBefore(g, s)
})()
