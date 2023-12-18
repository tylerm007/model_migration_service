select shp.shipid as "ShipID"
      ,to_char(shp.arrivaldate, 'yyyy-mm-dd') as "ArrivalDate"
      ,shp.location as "Location"
      ,shp.flt as "Flight"
      ,shp.awbnum as "Airwaybill"
      ,shp.pc as "PieceCount"
      ,trim(shp.rec) as "Received"
      ,nts.create_uid as "EmpNbr"
      ,to_char(nts.create_tmstp at time zone 'America/Toronto', 'yyyy-mm-dd HH24:MI:SS') as "Entered(ET)"
      ,nts.notes as "Notes"
  from @{SCHEMA}.ARI_023_SHIPMENTS shp
      ,@{SCHEMA}.ARI_023_NOTES nts
 where shp.shipid = nts.shipid (+)
   and to_char(shp.arrivaldate, 'yyyymmdd') >= '@{arg_yyyymmdd_from}'
   and to_char(shp.arrivaldate, 'yyyymmdd') <= '@{arg_yyyymmdd_to}'
 order by shp.arrivaldate
      ,shp.shipid
      ,nts.create_tmstp
