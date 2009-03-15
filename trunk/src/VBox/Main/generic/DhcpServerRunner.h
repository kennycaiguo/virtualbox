/* $Id$ */
/** @file
 * VirtualBox Main - interface for VBox DHCP server
 */

/*
 * Copyright (C) 2009 Sun Microsystems, Inc.
 *
 * This file is part of VirtualBox Open Source Edition (OSE), as
 * available from http://www.virtualbox.org. This file is free software;
 * you can redistribute it and/or modify it under the terms of the GNU
 * General Public License (GPL) as published by the Free Software
 * Foundation, in version 2 as it comes in the "COPYING" file of the
 * VirtualBox OSE distribution. VirtualBox OSE is distributed in the
 * hope that it will be useful, but WITHOUT ANY WARRANTY of any kind.
 *
 * Please contact Sun Microsystems, Inc., 4150 Network Circle, Santa
 * Clara, CA 95054 USA or visit http://www.sun.com if you need
 * additional information or have any questions.
 */
#include "DhcpServerImpl.h"
#include <iprt/err.h>
#include <iprt/types.h>
#include <VBox/com/string.h>

typedef enum
{
    DHCPCFG_NAME = 1,
    DHCPCFG_NETNAME,
    DHCPCFG_TRUNKTYPE,
    DHCPCFG_TRUNKNAME,
    DHCPCFG_MACADDRESS,
    DHCPCFG_IPADDRESS,
    DHCPCFG_LEASEDB,
    DHCPCFG_VERBOSE,
    DHCPCFG_BEGINCONFIG,
    DHCPCFG_GATEWAY,
    DHCPCFG_LOWERIP,
    DHCPCFG_UPPERIP,
    DHCPCFG_NETMASK,
    DHCPCFG_HELP,
    DHCPCFG_VERSION,
    DHCPCFG_NOTOPT_MAXVAL
}DHCPCFG;

#define TRUNKTYPE_WHATEVER "whatever"
#define TRUNKTYPE_NETFLT   "netflt"
#define TRUNKTYPE_NETADP   "netadp"
#define TRUNKTYPE_SRBNAT   "srvnat"

class DhcpServerRunner
{
public:
    DhcpServerRunner() : mProcess (NIL_RTPROCESS) {}
    ~DhcpServerRunner() { stop(); /* don't leave abandoned servers */}

    int setOption(DHCPCFG opt, char *val)
    {
        if(opt == 0 || opt >= DHCPCFG_NOTOPT_MAXVAL)
            return VERR_INVALID_PARAMETER;
        if(isRunning())
            return VERR_INVALID_STATE;

        mOptions[opt] = val;
        return VINF_SUCCESS;
    }

    int start();
    int stop();
    bool isRunning();
private:
    Utf8Str mOptions[DHCPCFG_NOTOPT_MAXVAL];
    RTPROCESS mProcess;
};
