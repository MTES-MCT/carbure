def certificate_site_xml_data(
    name="Some site",
    street_line="Some address",
    zipcode="12345",
    city="Some city",
    country_code="FR",
    main_site="true",
):
    return f"""\
<EO_CERTIFICATE_SITE>
  <SITE_NAME>{name}</SITE_NAME>
  <STREET_LINE>{street_line}</STREET_LINE>
  <POST_CODE>{zipcode}</POST_CODE>
  <CITY>{city}</CITY>
  <COUNTRY_CODE>{country_code}</COUNTRY_CODE>
  <MAIN_SITE>{main_site}</MAIN_SITE>
</EO_CERTIFICATE_SITE>"""
