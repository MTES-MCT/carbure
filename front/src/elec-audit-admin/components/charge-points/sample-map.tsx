import { ElecChargePointPreview } from "elec-audit-admin/types"
import { LatLngExpression } from "leaflet"
import 'leaflet-defaulticon-compatibility'
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css'; // Re-uses images from ~leaflet package
import 'leaflet/dist/leaflet.css'
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"



const ChargePointsSampleMap = ({ chargePoints }: { chargePoints: ElecChargePointPreview[] }) => {
  const franceCenterCoordinates: LatLngExpression = [46.2276, 2.2137]
  // bounds https://react-leaflet.js.org/docs/example-view-bounds/
  return (
    <MapContainer center={franceCenterCoordinates} zoom={5} style={{ height: '350px', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {chargePoints.map((point, idx) => (
        <Marker key={idx} position={[point.latitude, point.longitude]} >
          <Popup>ID : {point.charge_point_id}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};


export default ChargePointsSampleMap
