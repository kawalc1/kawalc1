package id.kawalc1.clients

import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1
import id.kawalc1.{KelurahanOld, KelurahanResponse, PresidentialLembar2, SingleSum}
import org.json4s.native.Serialization
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.{Matchers, WordSpec}

import scala.io.Source

class KawalRC1CliRentSpecs extends WordSpec with Matchers with ScalaFutures with ScalatestRouteTest with JsonSupport {
  "KawalC1Client" should {

    "parse the `1101052008.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/1101052008.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 3
      set.head._1 shouldBe 1
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "11010520081"
      firstTps.name shouldBe "1"
    }

    "parse the `1101012001.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/1101012001.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 3
      set.head._1 shouldBe 1
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "11010120011"
      firstTps.name shouldBe "1"

      val lastTps: kawalc1.TpsInfo = set.last._2.head
      lastTps.idLokasi shouldBe "11010120013"
      lastTps.pendingUploads.get.head._1 shouldBe "5nCvPsP2YiQ1IqpdBnnt"
    }

    "parse the `1101012002.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/1101012002.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 2
      set.head._1 shouldBe 1
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "11010120021"
      firstTps.name shouldBe "1"

      val lastTps: kawalc1.TpsInfo = set.last._2.head
      lastTps.idLokasi shouldBe "11010120022"
      lastTps.pendingUploads.get.head._1 shouldBe "OdPjJsgCNa3x2PVAMIFT"
    }

    "parse the `5171021003.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/5171021003.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 4
      set.head._1 shouldBe 1
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "51710210031"
      firstTps.name shouldBe "1"

      val lastTps: kawalc1.TpsInfo = set.last._2.head
      lastTps.idLokasi shouldBe "62080220041"
      lastTps.pendingUploads.get.head._1 shouldBe "pzQbcMvsX2AmEHdUbhTB"
    }

    "parse the `4.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/4.json")).mkString
      val kelurahan = Serialization.read[KelurahanOld](response)
      kelurahan.data.keySet.size shouldBe 3
      val tps = kelurahan.data(1)
      tps.photos.keySet.size shouldBe 7
      val verification = tps.photos.head._2
//      verification.sum.get shouldBe SingleSum(25)
    }

    "parse the `20780.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/api/c/20780.json")).mkString
      val kelurahan = Serialization.read[KelurahanOld](response)
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
