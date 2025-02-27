import { NextRequest, NextResponse } from "next/server";
import { analyzePlots } from "@/utils/analizePlots";
import { isValidWkt } from "@/utils/validateWkt";
import { withErrorHandling } from "@/lib/hooks/withErrorHandling";
import { withRequiredJsonBody } from "@/lib/hooks/withRequiredJsonBody";
import { useBadRequestResponse } from "@/lib/hooks/responses";
import { LogFunction } from "@/lib/logger";
import { withLogging } from "@/lib/hooks/withLogging";
import { compose } from "@/utils/compose";
import { wktToFeatureCollection } from "@/utils/wktUtils";
import { createLog } from "@/lib/auth/db";

export const POST = compose(
  withLogging,
  withErrorHandling,
  withRequiredJsonBody
)(async (req: NextRequest, log: LogFunction, body: any): Promise<NextResponse> => {
  const generateGeoids = body.generateGeoids || false;
  const { wkt } = body;
  const userId = req.headers.get("X-User-ID");

  if (!wkt) return useBadRequestResponse("Missing attribute 'wkt'");

  const isValidWKT = isValidWkt(wkt);
  if (!isValidWKT) return useBadRequestResponse("Invalid WKT.");

  let featureCollection = await wktToFeatureCollection(wkt, generateGeoids) as object;
  featureCollection = { ...featureCollection, generateGeoids };
  
  // Log the request details if user is authenticated
  if (userId) {
    createLog({
      userId,
      endpoint: "/api/wkt",
      requestData: JSON.stringify({ wkt: wkt.substring(0, 100) + "..." }), // Truncate WKT for log
      responseStatus: 200,
    });
  }
  
  return await analyzePlots(featureCollection, log);
});
