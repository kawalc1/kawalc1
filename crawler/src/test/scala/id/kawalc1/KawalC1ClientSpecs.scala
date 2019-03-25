package id.kawalc1

import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1.clients.{ JsonSupport, Kelurahan, PresidentialLembar2, Verification }
import org.json4s.native.Serialization
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.{ Matchers, WordSpec }

import scala.io.Source

class KawalC1ClientSpecs extends WordSpec with Matchers with ScalaFutures with ScalatestRouteTest with JsonSupport {
  "KawalC1Client" should {
    "parse the response" in {
      val response = Source.fromURL(getClass.getResource("/api/c/5.json")).mkString
      val kelurahan = Serialization.read[Kelurahan](response)
      kelurahan.data.keySet.size shouldBe 1
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 1
      val verification = tps.photos.head._2
      verification.sum.get shouldBe PresidentialLembar2(100, 100, 200, 3)
    }
  }
}