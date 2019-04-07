package id.kawalc1.database

import enumeratum.values.SlickValueEnumSupport
import slick.jdbc.SQLiteProfile.api._
import slick.lifted.Tag

case class AlignResult(id: Int,
                       tps: Int,
                       photo: String,
                       photoSize: Int,
                       alignQuality: Int,
                       config: String,
                       alignedUrl: Option[String],
                       extracted: Option[Boolean])

case class ExtractResult(
    id: Int,
    tps: Int,
    photo: String,
    response: String,
    digitArea: String,
    tpsArea: String
)

object ResultsTables extends SlickValueEnumSupport {
  val profile = slick.jdbc.SQLiteProfile

  class AlignResults(tag: Tag) extends Table[AlignResult](tag, "align_results") {
    def id           = column[Int]("kelurahan")
    def tps          = column[Int]("tps")
    def photo        = column[String]("photo", O.PrimaryKey)
    def photoSize    = column[Int]("photo_size")
    def alignQuality = column[Int]("align_quality")
    def config       = column[String]("config")
    def alignedUrl   = column[Option[String]]("aligned_url")
    def extracted    = column[Option[Boolean]]("extracted")

    override def * =
      (id, tps, photo, photoSize, alignQuality, config, alignedUrl, extracted) <> (AlignResult.tupled, AlignResult.unapply)
  }

  val resultsQuery = TableQuery[AlignResults]

  class ExtractResults(tag: Tag) extends Table[ExtractResult](tag, "extract_results") {
    def id        = column[Int]("kelurahan")
    def tps       = column[Int]("tps")
    def photo     = column[String]("photo", O.PrimaryKey)
    def response  = column[String]("response")
    def digitArea = column[String]("digit_area")
    def tpsArea   = column[String]("tps_area")

    override def * =
      (id, tps, photo, response, digitArea, tpsArea) <> (ExtractResult.tupled, ExtractResult.unapply)
  }

  val extractResultsQuery = TableQuery[ExtractResults]

  def upsertAlign(results: Seq[AlignResult]) = {
    results.map(resultsQuery.insertOrUpdate)
  }

  def upsertExtract(results: Seq[ExtractResult]) = {
    results.map(extractResultsQuery.insertOrUpdate)
  }
}
