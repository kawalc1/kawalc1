package id.kawalc1.clients

import akka.http.scaladsl.testkit.ScalatestRouteTest
import id.kawalc1
import id.kawalc1.{FormType, Kelurahan, KelurahanOld, KelurahanResponse, Plano, PresidentialLembar2, SingleSum}
import org.json4s.native.Serialization
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.{Matchers, WordSpec}

import scala.io.Source

class KawalRC1CliRentSpecs extends WordSpec with Matchers with ScalaFutures with ScalatestRouteTest with JsonSupport {
  "KawalC1Client" should {

    "parse the `9671101003.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/9671101003.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 1
      set.head._1 shouldBe "4"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "96711010034"
      firstTps.name shouldBe "4"
      val photos = Kelurahan.toPhotoTps(kelurahan)
      photos.length shouldBe 2

      val firstPhoto = photos.head
      firstPhoto.uploadedPhotoId shouldBe "KmhfLGxXVZ8DpUchkVBW"
      Plano.withValue(firstPhoto.plano.get) shouldBe Plano.YES
      FormType.withValue(firstPhoto.formType.get) shouldBe FormType.KPU
      firstPhoto.pas2 shouldBe Some(67)
      firstPhoto.pas2Agg shouldBe Some(67)

      val secondPhoto = photos.tail.head
      secondPhoto.uploadedPhotoId shouldBe "DE8dJrzeE09sYKN4vQ6N"
    }

    "parse the `3173041007.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/3173041007.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 1
      set.head._1 shouldBe "2"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "31730410072"
      firstTps.name shouldBe "2"
      val photos = Kelurahan.toPhotoTps(kelurahan)
      photos.length shouldBe 2

      val firstPhoto = photos.head
      firstPhoto.uploadedPhotoId shouldBe "t132HpVYDRZXSyReRu5q"
      Plano.withValue(firstPhoto.plano.get) shouldBe Plano.YES
      FormType.withValue(firstPhoto.formType.get) shouldBe FormType.KPU
      firstPhoto.pas2 shouldBe Some(123)
      firstPhoto.pas2Agg shouldBe Some(89)

      val secondPhoto = photos.tail.head
      secondPhoto.uploadedPhotoId shouldBe "fscl0Nami6cmicH1n93i"
      Plano.withValue(secondPhoto.plano.get) shouldBe Plano.YES
      secondPhoto.formType shouldBe None
      secondPhoto.pas2 shouldBe Some(356)
      secondPhoto.pas2Agg shouldBe Some(89)

    }

    "parse the `9408042004.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/9408042004.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 5
      set.head._1 shouldBe "4"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "94080420044"
      firstTps.name shouldBe "4"
      val photos = Kelurahan.toPhotoTps(kelurahan)
      photos.length shouldBe 2

      val firstPhoto = photos.head
      firstPhoto.uploadedPhotoId shouldBe "rNWNu52aJHXDVKmVIhhT"
      Plano.withValue(firstPhoto.plano.get) shouldBe Plano.YES
      firstPhoto.formType shouldBe None

      val secondPhoto = photos.tail.head
      secondPhoto.uploadedPhotoId shouldBe "ukr66utXx0fhf4gwzhb5"
      Plano.withValue(secondPhoto.plano.get) shouldBe Plano.YES
      secondPhoto.formType shouldBe None
    }

    "parse the `990505.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/990505.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 3
      set.head._1 shouldBe "9905050001"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "9905050001"
      firstTps.name shouldBe "KSK"
      Kelurahan.toPhotoTps(kelurahan).length shouldBe 0
    }

    "parse the `1101052008.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/1101052008.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 3
      set.head._1 shouldBe "1"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "11010520081"
      firstTps.name shouldBe "1"
    }

    "parse the `1101012001.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/1101012001.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 3
      set.head._1 shouldBe "1"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "11010120011"
      firstTps.name shouldBe "1"

      val lastTps: kawalc1.TpsInfo = set.last._2.head
      lastTps.idLokasi shouldBe "11010120013"
      lastTps.pendingUploads.get.head._1 shouldBe "5nCvPsP2YiQ1IqpdBnnt"
      Kelurahan.toPhotoTps(kelurahan).length shouldBe 7
      val tpses = Kelurahan.toTps(kelurahan)
      tpses.length shouldBe 3
      tpses.head.uploadedPhotoUrl shouldBe None
    }

    "parse the `1101012002.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/1101012002.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 2
      set.head._1 shouldBe "1"
      val firstTps = set.head._2.head
      firstTps.idLokasi shouldBe "11010120021"
      firstTps.name shouldBe "1"

      val lastTps: kawalc1.TpsInfo = set.last._2.head
      lastTps.idLokasi shouldBe "11010120022"
      lastTps.pendingUploads.get.head._1 shouldBe "OdPjJsgCNa3x2PVAMIFT"

      Kelurahan.toPhotoTps(kelurahan).length shouldBe 0
      Kelurahan.toTps(kelurahan).length shouldBe 2
    }

    "parse the `5171021003.json` response" in {
      val response  = Source.fromURL(getClass.getResource("/hierarchy/5171021003.json")).mkString
      val kelurahan = Serialization.read[KelurahanResponse](response)
      val set       = kelurahan.result.aggregated
      set.keySet.size shouldBe 4
      set.head._1 shouldBe "1"
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
