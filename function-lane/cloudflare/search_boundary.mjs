function toRad(deg){ return Number(deg)*Math.PI/180; }

export function distanceKm(a={},b={}){
  const lat1=Number(a.lat), lon1=Number(a.lon ?? a.long);
  const lat2=Number(b.lat), lon2=Number(b.lon ?? b.long);
  if(![lat1,lon1,lat2,lon2].every(Number.isFinite)) return null;
  const R=6371.0088;
  const dLat=toRad(lat2-lat1);
  const dLon=toRad(lon2-lon1);
  const s1=Math.sin(dLat/2);
  const s2=Math.sin(dLon/2);
  const h=s1*s1+Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*s2*s2;
  return 2*R*Math.asin(Math.min(1,Math.sqrt(h)));
}

function boundaryKm(boundary={}){
  const value=Number(boundary.value);
  if(!Number.isFinite(value) || value<0) return null;
  const unit=String(boundary.unit??"").toLowerCase();
  if(/^km|kilomet/.test(unit)) return value;
  if(/^mile/.test(unit)) return value*1.609344;
  return null;
}

export function checkDistanceBoundary(originCoords={},candidateCoords={},boundary={}){
  const limitKm=boundaryKm(boundary);
  const measuredKm=distanceKm(originCoords,candidateCoords);
  if(limitKm===null) return {ok:false,function:"SEARCH_DISTANCE_BOUNDARY",error:"BAD_BOUNDARY"};
  if(measuredKm===null) return {ok:false,function:"SEARCH_DISTANCE_BOUNDARY",error:"BAD_COORDINATES"};
  const operator=String(boundary.operator??"<=");
  const pass=operator==="<=" ? measuredKm<=limitKm
    : operator==="<" ? measuredKm<limitKm
    : operator===">=" ? measuredKm>=limitKm
    : operator===">" ? measuredKm>limitKm
    : false;
  return {
    ok:true,
    function:"SEARCH_DISTANCE_BOUNDARY",
    pass,
    operator,
    limit_km:limitKm,
    measured_km:Math.round(measuredKm*10)/10
  };
}
