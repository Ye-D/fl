from Common.Server.fl_grpc_server import FlGrpcServer
from Common.Grpc.fl_grpc_pb2 import GradResponse_float
from Common.Handler.handler import Handler

import Common.config as config

import numpy as np


class ClearMedianServer(FlGrpcServer):
    def __init__(self, address, port, config, handler):
        super(ClearMedianServer, self).__init__(config=config)
        self.address = address
        self.port = port
        self.config = config
        self.handler = handler

    def UpdateGrad_float(self, request, context): # using Median
        data_dict = {request.id: request.grad_ori}
        print("have received:", data_dict.keys())
        rst = super().process(dict_data=data_dict, handler=self.handler.computation)
        return GradResponse_float(grad_upd=rst)


class MedianGradientHandler(Handler):
    def __init__(self, num_workers, f):
        super(MedianGradientHandler, self).__init__()
        self.num_workers = num_workers
        self.f = f

    def computation(self, data_in):
        grad_in = np.array(data_in).reshape((self.num_workers, -1))
        grad_tmp = np.sort(grad_in, axis=0)
        grad_agg = grad_tmp[self.num_workers // 2]
        
        return grad_agg.tolist()


if __name__ == "__main__":
    gradient_handler = MedianGradientHandler(num_workers=config.num_workers, f = config.f)

    median_server = ClearMedianServer(address=config.server1_address, port=config.port1, config=config,
                                    handler=gradient_handler)
    median_server.start()
