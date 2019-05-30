package id.kawalc1

package object clients {
  case class StringValue(
    stringValue: String)
  case class Photo(
    url: StringValue)
  case class PhotoFields(
    fields: Photo)
  case class PhotoSet(
    mapValue: PhotoFields)
  case class Fields(
    fields: Map[String, PhotoSet])
  case class DocFields(
    mapValue: Fields)
  case class Images(
    images: DocFields)

  case class Document(
    fields: Images)

  case class PhotoCombi(
    photo: String,
    imageId: String)

}
