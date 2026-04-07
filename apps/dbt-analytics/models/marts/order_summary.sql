with orders as (
    select * from {{ ref('stg_orders') }}
),
products as (
    select
        id as product_id,
        price
    from {{ source('shop', 'products') }}
)
select
    o.customer_id,
    count(o.order_id)                              as total_orders,
    sum(o.quantity * p.price)                      as total_spend,
    max(o.order_date)                              as last_order_date
from orders o
join products p on o.product_id = p.product_id
group by 1
