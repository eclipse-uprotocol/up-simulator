package org.eclipse.uprotocol.service.androidproxy.vehicleservice;

import com.google.protobuf.Descriptors;

import org.covesa.uservice.vehicle.body.cabin_climate.v1.CabinClimateService;
import org.covesa.uservice.vehicle.chassis.suspension.v1.SuspensionService;
import org.eclipse.uprotocol.service.androidproxy.BaseService;
import org.eclipse.uprotocol.service.androidproxy.utils.Constants;

public class Suspension extends BaseService {
    Descriptors.ServiceDescriptor serviceDescriptor = SuspensionService.getDescriptor().findServiceByName("Suspension");

    @Override
    public void onCreate() {
        super.onCreate();
        initializeUPClient(serviceDescriptor);
    }

}
