package id.kawalc1.clients

import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1.{Kelurahan, PresidentialLembar2, SingleSum}
import org.json4s.native.Serialization
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.{Matchers, WordSpec}

import scala.io.Source

class KawalRC1CliRentSpecs extends WordSpec with Matchers with ScalaFutures with ScalatestRouteTest with JsonSupport {
  "KawalC1Client" should {

    "parse the `5.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/5.json")).mkString
      val kelurahan = Serialization.read[Kelurahan](response)
      kelurahan.data.keySet.size shouldBe 1
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 1
      val verification = tps.photos.head._2
      verification.sum.get shouldBe PresidentialLembar2(100, 100, 200, 3)
    }

    "parse the `4.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/4.json")).mkString
      val kelurahan = Serialization.read[Kelurahan](response)
      kelurahan.data.keySet.size shouldBe 3
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 7
      val verification = tps.photos.head._2
      verification.sum.get shouldBe SingleSum(25)
    }

    "parse the `58044.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/58044.json")).mkString
      val kelurahan = Serialization.read[Kelurahan](response)
      kelurahan.data.keySet.size shouldBe 3
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 4
      val verification = tps.photos.head._2
      verification.sum.get shouldBe PresidentialLembar2(456, 123, 579, 2)
    }

    "parse the `82193.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/82193.json")).mkString
      val kelurahan = Serialization.read[Kelurahan](response)
      kelurahan.data.keySet.size shouldBe 3
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 4
      val verification = tps.photos.head._2
      verification.sum.get shouldBe PresidentialLembar2(456, 123, 579, 2)
    }
    "parse the `20780.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/20780.json")).mkString
      val kelurahan = Serialization.read[Kelurahan](response)
      kelurahan.data.keySet.size shouldBe 17
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 2
      val verification = tps.photos.head._2
      verification.sum.get shouldBe SingleSum(199)
      val second = tps.photos.tail.head._2
      second.sum.get shouldBe PresidentialLembar2(59, 121, 180, 19)
    }
  }
}
