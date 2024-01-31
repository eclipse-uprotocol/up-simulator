package org.eclipse.uprotocol.service.androidproxy.vehicleservice;

import com.google.protobuf.Descriptors;

import org.covesa.uservice.vehicle.body.cabin_climate.v1.CabinClimateService;
import org.eclipse.uprotocol.service.androidproxy.BaseService;

public class CabinClimate extends BaseService {
    Descriptors.ServiceDescriptor serviceDescriptor = CabinClimateService.getDescriptor().findServiceByName("BodyCabinclimate");

    @Override
    public void onCreate() {
        super.onCreate();
        initializeUPClient(serviceDescriptor);
    }

}
