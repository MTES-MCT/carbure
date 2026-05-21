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
  <MASS_BALANCE_START_DATE>2026-01-08Z</MASS_BALANCE_START_DATE>
  <MASS_BALANCE_DURATION>12</MASS_BALANCE_DURATION>
  <EO_SITE_SCOPE>
    <ORGANISATION_SCOPE>BG</ORGANISATION_SCOPE>
    <IN_MATERIAL>URWR001</IN_MATERIAL>
    <OUT_MATERIAL>FBM0003</OUT_MATERIAL>
    <PROD_PLANT_DATE>2026-02-11Z</PROD_PLANT_DATE>
    <GHG>
      <GHG>AV</GHG>
    </GHG>
  </EO_SITE_SCOPE>
</EO_CERTIFICATE_SITE>"""
