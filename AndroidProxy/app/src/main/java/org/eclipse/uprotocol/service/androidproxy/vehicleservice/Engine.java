package org.eclipse.uprotocol.service.androidproxy.vehicleservice;

import com.google.protobuf.Descriptors;

import org.covesa.uservice.vehicle.body.cabin_climate.v1.CabinClimateService;
import org.covesa.uservice.vehicle.propulsion.engine.v1.EngineService;
import org.eclipse.uprotocol.service.androidproxy.BaseService;
import org.eclipse.uprotocol.service.androidproxy.utils.Constants;

public class Engine extends BaseService {
    Descriptors.ServiceDescriptor serviceDescriptor = EngineService.getDescriptor().findServiceByName("Engine");

    @Override
    public void onCreate() {
        super.onCreate();
        initializeUPClient(serviceDescriptor);
    }

}
