// WAREHOUSE CLOSED-LOOP RECEIPT GATE
// Emit one compact receipt only after DONE is verified, trace is married to one original,
// and temporary communication copies are clean. This is the final proof that the loop is closed.

export function warehouseClosedLoopReceiptGate({jobId='',doneState='',marriageState='',copyState='',originalRef=null,traceRef=null}={}) {
  const ready=doneState==='job-done-verified' && marriageState==='loop-closed' && copyState==='copy-loops-clean' && !!originalRef && !!traceRef;
  return {warehouseClosedLoopReceipt:{
    receipt:ready?{jobId,originalRef,traceRef,status:'CLOSED'}:null,
    state:ready?'closed-loop-receipt-ready':'loop-still-open',
    action:ready?'file-receipt-in-warehouse':'return-to-open-joint',
    rule:'DO NOT CALL THE JOB CLOSED UNTIL DONE, ORIGINAL, TRACE, AND TEMPORARY COPIES ALL AGREE'
  }};
}
