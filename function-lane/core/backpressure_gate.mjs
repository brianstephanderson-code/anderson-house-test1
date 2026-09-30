// BACKPRESSURE GATE
// Slow only the overloaded branch. Do not stop unrelated hive work.

export function backpressureGate({basketId='',queued=0,processingCapacity=1,highWaterMark=10,lowWaterMark=3,currentlyPaused=false}={}) {
  const capacity=Math.max(1,processingCapacity);
  const pressure=queued/capacity;
  let action='feed';

  if (currentlyPaused) action=queued<=lowWaterMark?'resume-feed':'hold-feed';
  else if (queued>=highWaterMark) action='pause-feed';

  return {
    backpressure:{
      basketId,queued,processingCapacity:capacity,pressure,action,
      scope:'local-basket-only',
      rule:'SLOW THE CLOGGED BASKET, NOT THE WHOLE HIVE'
    }
  };
}
