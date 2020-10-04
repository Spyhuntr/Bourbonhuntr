

query = (
'''
select 
    bourbon.storeid,
    store_full_addr,
    bourbon.productid,
    description,
    quantity,
    insert_dt
from bourbon
inner join bourbon_desc
on bourbon.productid = bourbon_desc.productid
inner join bourbon_stores
on bourbon.storeid = bourbon_stores.storeid
where CAST(insert_dt AS DATE) >= %s
and CAST(insert_dt AS DATE) <= %s
order by bourbon.storeid

'''
)



stores_query = (
'''
select 
    storeid,
    Concat(storeid, '-', store_addr_2, ' ', store_city) as store_addr
    from bourbon_stores
    order by length(storeid)
'''

)

product_query = (
'''
select productid, description from bourbon_desc order by description
'''

)


tot_inv_query = (
'''
select 
	CAST(insert_dt AS DATE) insert_dt,
	SUM(quantity) quantity
from bourbon
where CAST(insert_dt AS DATE) >= '2020-03-01'
GROUP BY CAST(insert_dt AS DATE)
'''
)


map_query = (
'''
select 
latitude,
longitude,
sum(quantity) as quantity
from bourbon
group by latitude, longitude
'''
)