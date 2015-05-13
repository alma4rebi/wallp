import socket

from .proto.client_pb2 import Request
from .proto.server_pb2 import Response
from .server.message_length_helper import MessageReceiver, prefix_message_length


class ServerImageException(Exception):
	def __init__(self, message, retry=False):
		Exception.__init__(self, message)
		self.retry = retry


class ServerImageNotChanged(ServerImageException):
	def __init__(self, message):
		ServerImageException.__init__(self, message, retry=False)


#a class to talk to wallp server
class WallpServer(Service):
	def __init__(self):
		self._host = ''
		self._port = 40001


	def get_image(self):
		retries = 3

		while retries > 0:
			try:
				self.update_frequency()
				if not self.has_image_changed():
					raise ServerImageNotChanged('server image is unchanged')

				self.get_image_from_server()

			except (ServerImageException, ServerImageNotChanged) as e:
				print e.message
				if e.retry:
					retries -= 1
				else:
					raise ServiceException()

	def update_frequency(self):
		request = Request()
		request.type = Request.FREQUENCY

		self.send_request(request)
		response = self.recv_response()

		#extract frequency and store it, db


	def has_image_changed(self):
		request = Request()
		request.type = Request.LAST_CHANGE

		self.send_request(request)
		response = self.recv_response()

		last_change = response.last_change

		#get last change from db and compare

		return True


	
	def start_connection(self):
		self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._connection.connect((self._host, self._port))
		self._msg_receiver = MessageReceiver(blocking=True)


	def send_request(self, request):
		self._connection.send(prefix_message_length(request.SerializeToString()))	#exc


	def recv_response(self)
		message = self._msg_receiver.recv(self._connection)

		response = Response()
		response.ParseFromString(message)	#exc

		return response


	def get_image_info(self, response):
		extension = response.image_info.extension
		length = response.image_info.length
		chunk_count = response.image_info.chunk_count

		return extension, length, chunk_count	


	def read_image_bytes(self, length, chunk_count):
		response = self.recv_response()
		temp_image_path = 'tmp12314'

		image_file = open(temp_image_path, 'wb')

		while chunk_count > 0:
			exception = None

			if response.type == Response.IMAGE_CHUNK:
				chunk = response.image_chunk.data
				image_file.write(chunk)

			elif response.type == Response.IMAGE_ABORT:
				exception = ServerImageException('server image changed, abort current image; restart', retry=True)

			else:
				exception = ServerImageException('unexpected response type when expecting image chunk')

			if exception is not None:
				image_file.close()
				os.remove(temp_image_path)
				raise exception

			chunk_count -= 1

		image_file.close()
		self.check_recvd_image_size(length, temp_image_path)

		return temp_image_path


	def check_recvd_image_size(self, expected_size, image_path):
		recvd_size = os.stat(image_path).st_size
		if recvd_size != expected_size:
			os.remove(image_path)
			raise ServerImageException('received image size mismatch, expected: %d, received: %d'%(expected_size, recvd_size))


	def retry_image(self):
		retries = 3
		sleep_time = 20

		request = Request()
		request.type = Request.IMAGE

		while retries > 0:
			sleep(sleep_time)
			print 'retrying server..'
			self.send_request(request)
			response = self.recv_response()

			if response.type != Response.IMAGE_CHANGING:
				return response

			retries -= 1
			sleep_time *= 2

		raise ServerImageException('server image is changing for a long time; giving up')


	def get_image_from_server(self):
		extension = None
		length = None
		chunk_count = None

		request = Request()
		request.type = Request.IMAGE
		self.send_request(request)
		response = self.recv_response()

		if response.type == Response.IMAGE_CHANGING:
			response = self.retry_image()

		if response.type == Response.IMAGE_NONE:
			raise ServerImageException('no image set on server')

		elif response.type == Response.IMAGE_INFO:
			extension, length, chunk_count = self.get_image_info()
			temp_image_path = self.read_image_bytes()
			return extension, temp_image_path
			
		else:
			raise ServerImageException('bad response', retry=True)