#_*_coding:utf-8_*_
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()


channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')
# exclusive=True 唯一的
# 不指定queue名字,rabbit会随机分配一个名字,
# exclusive=True会在使用此queue的消费者断开后,自动将queue删除
result = channel.queue_declare(queue='',exclusive=True)

# 随机取queue名字。
queue_name = result.method.queue
print("random queuename",queue_name)

# channel.queue_bind 绑定exchange转发器
# exchange=logs 由于rabbitMQ下不知一个exchange需要绑定。
#　queue_name　对列名
channel.queue_bind(exchange='logs',
                   queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(queue=queue_name,
                      on_message_callback=callback,
                      auto_ack=True)

channel.start_consuming()