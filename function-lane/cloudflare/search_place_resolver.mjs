function clean(v=""){ return String(v??"").replace(/\s+/g," ").trim(); }

export function normalizePlaceResult(item={},provider="UNKNOWN"){
  const lat=Number(item.latitude ?? item.lat);
  const lon=Number(item.longitude ?? item.lon);
  return {
    name:clean(item.name ?? item.display_name ?? ""),
    lat:Number.isFinite(lat)?lat:null,
    lon:Number.isFinite(lon)?lon:null,
    country:clean(item.country ?? ""),
    country_code:clean(item.country_code ?? item.country_code_iso2 ?? ""),
    admin1:clean(item.admin1 ?? ""),
    timezone:clean(item.timezone ?? ""),
    provider
  };
}

export async function resolvePlaceOpenMeteo(name,{countryCode=null,count=3,fetchImpl=fetch}={}){
  const q=clean(name);
  if(!q) return {ok:false,function:"SEARCH_PLACE_RESOLVER",error:"EMPTY_PLACE",provider:"OPEN_METEO_GEOCODING",results:[]};

  const url=new URL("https://geocoding-api.open-meteo.com/v1/search");
  url.searchParams.set("name",q);
  url.searchParams.set("count",String(Math.max(1,Math.min(Number(count)||3,10))));
  url.searchParams.set("language","en");
  url.searchParams.set("format","json");
  if(countryCode) url.searchParams.set("countryCode",String(countryCode).toUpperCase());

  let response;
  try {
    response=await fetchImpl(url.toString(),{headers:{accept:"application/json"}});
  } catch(e) {
    return {ok:false,function:"SEARCH_PLACE_RESOLVER",error:"FETCH_FAILED",detail:String(e?.message??e),provider:"OPEN_METEO_GEOCODING",results:[]};
  }
  if(!response?.ok) return {ok:false,function:"SEARCH_PLACE_RESOLVER",error:`HTTP_${response?.status??"UNKNOWN"}`,provider:"OPEN_METEO_GEOCODING",results:[]};

  let body;
  try { body=await response.json(); }
  catch { return {ok:false,function:"SEARCH_PLACE_RESOLVER",error:"BAD_JSON",provider:"OPEN_METEO_GEOCODING",results:[]}; }

  const results=(Array.isArray(body?.results)?body.results:[])
    .map(x=>normalizePlaceResult(x,"OPEN_METEO_GEOCODING"))
    .filter(x=>Number.isFinite(x.lat)&&Number.isFinite(x.lon));

  return {
    ok:results.length>0,
    function:"SEARCH_PLACE_RESOLVER",
    provider:"OPEN_METEO_GEOCODING",
    query:q,
    provenance:"https://geocoding-api.open-meteo.com/v1/search",
    attribution:"Location data based on GeoNames via Open-Meteo",
    results
  };
}

export async function resolvePlace(name,options={}){
  const provider=String(options.provider??"OPEN_METEO_GEOCODING").toUpperCase();
  if(provider==="OPEN_METEO_GEOCODING") return resolvePlaceOpenMeteo(name,options);
  return {ok:false,function:"SEARCH_PLACE_RESOLVER",error:"UNSUPPORTED_PROVIDER",provider,results:[]};
}
