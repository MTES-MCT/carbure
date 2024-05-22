import { ElecChargePointPreview } from "elec-audit-admin/types"
import { LatLngExpression, icon } from "leaflet"
import mapPinSVG from "carbure/assets/images/map-pin.svg"
import "leaflet-defaulticon-compatibility"
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css" // Re-uses images from ~leaflet package
import "leaflet/dist/leaflet.css"
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"

const ChargePointsSampleMap = ({
  chargePoints,
}: {
  chargePoints?: ElecChargePointPreview[]
}) => {
  const franceCenterCoordinates: LatLngExpression = [46.2276, 2.2137]
  // bounds https://react-leaflet.js.org/docs/example-view-bounds/
  return (
    <MapContainer
      center={franceCenterCoordinates}
      zoom={5}
      style={{ height: "350px", width: "100%" }}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {chargePoints?.map((point, idx) => (
        <Marker
          key={idx}
          position={[point.latitude, point.longitude]}
          icon={icon({
            iconUrl: mapPinSVG,
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
          })}
        >
          <Popup>
            <div>ID : {point.charge_point_id}</div>
            <div>
              {point.latitude}, {point.longitude}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}

export default ChargePointsSampleMap
