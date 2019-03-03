package kawalc1

import io.gatling.core.Predef._
import io.gatling.http.Predef._

import scala.concurrent.duration._

class KawalC1Simulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://kawalc1.appspot.com") // Here is the root for all relative URLs
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8") // Here are the common headers
    .acceptEncodingHeader("gzip, deflate")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .userAgentHeader("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20100101 Firefox/16.0")


  val digitizeRequest =
    http("digitize_1")
      .get("/download/1/13/3.JPG")

  val alignScenario =
    scenario("Digitizing image")
      .exec(digitizeRequest)

  setUp(
    alignScenario.inject(constantUsersPerSec(100) during (30 minutes)).throttle(
      reachRps(100) in (60 seconds),
      holdFor(1 minutes),
      jumpToRps(200),
      holdFor(1 minutes)
    ).protocols(httpProtocol))
}
