from zope.interface import implements
import struct

from ..imported.twisted.internet_interfaces import IPullProducer
from ..server_helper import get_limits
from ..proto.server_pb2 import Response


class ImageChunkProducer:
	implements(IPullProducer)

	def __init__(self, transport, wp_image):
		self._transport = transport
		self._wp_image = wp_image
		self._chunk_no = 0


	def stopProducing(self):
		if self._chunk_no < self._wp_image.chunk_count:
			response - Response()
			response.type = IMAGE_ABORT

			message = response.SerializetoString()
			message = struct.pack('>i', len(message)) + message

			self._transport.write(message)

		self._transport.unregisterProducer()


	def resumeProducing(self):
		if self._chunk_no < self._wp_image.chunk_count:
			response = Response()
			response.type = Response.IMAGE_CHUNK
			response.image_chunk.data = self._wp_image.chunk(self._chunk_no)

			message = response.SerializeToString()
			message = struct.pack('>i', len(message)) + message

			self._transport.write(message)

			self._chunk_no += 1
		else:
			self.stopProducing()
		
