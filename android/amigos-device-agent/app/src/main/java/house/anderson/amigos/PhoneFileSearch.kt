package house.anderson.amigos

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.DocumentsContract
import java.util.ArrayDeque

object PhoneFileAccess {
    private const val PREFS = "phone_file_access"
    private const val KEY_TREE_URI = "tree_uri"

    fun treeUri(context: Context): Uri? =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY_TREE_URI, null)
            ?.let(Uri::parse)

    fun grant(context: Context, uri: Uri, resultFlags: Int) {
        val takeFlags = resultFlags and
            (Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        context.contentResolver.takePersistableUriPermission(
            uri,
            takeFlags and Intent.FLAG_GRANT_READ_URI_PERMISSION
        )
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_TREE_URI, uri.toString())
            .apply()
    }

    fun snapshot(context: Context): String {
        val uri = treeUri(context)
        return if (uri == null) {
            "PHONE FILE DOOR\nFolder granted: false"
        } else {
            "PHONE FILE DOOR\nFolder granted: true\nTree: $uri"
        }
    }
}

object PhoneFileSearch {
    private const val MAX_FILES = 10000
    private const val MAX_MATCHES = 100
    private const val MAX_TEXT_BYTES = 8L * 1024L * 1024L

    private data class Pending(
        val documentId: String,
        val path: String
    )

    fun search(context: Context, rawQuery: String): String {
        val query = rawQuery.trim()
        if (query.isEmpty()) return "Enter something to search for."

        val treeUri = PhoneFileAccess.treeUri(context)
            ?: return "No folder has been granted yet."

        val resolver = context.contentResolver
        val rootId = try {
            DocumentsContract.getTreeDocumentId(treeUri)
        } catch (_: Throwable) {
            return "The saved folder permission is not usable. Choose the folder again."
        }

        val stack = ArrayDeque<Pending>()
        stack.add(Pending(rootId, ""))
        val hits = mutableListOf<String>()
        var filesSeen = 0
        var foldersSeen = 0

        while (stack.isNotEmpty() && filesSeen < MAX_FILES && hits.size < MAX_MATCHES) {
            val current = stack.removeLast()
            val childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(
                treeUri,
                current.documentId
            )

            try {
                resolver.query(
                    childrenUri,
                    arrayOf(
                        DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                        DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                        DocumentsContract.Document.COLUMN_MIME_TYPE,
                        DocumentsContract.Document.COLUMN_SIZE
                    ),
                    null,
                    null,
                    null
                )?.use { cursor ->
                    val idCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DOCUMENT_ID)
                    val nameCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DISPLAY_NAME)
                    val mimeCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_MIME_TYPE)
                    val sizeCol = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_SIZE)

                    while (cursor.moveToNext() && filesSeen < MAX_FILES && hits.size < MAX_MATCHES) {
                        val childId = cursor.getString(idCol)
                        val name = cursor.getString(nameCol) ?: "(unnamed)"
                        val mime = cursor.getString(mimeCol) ?: ""
                        val size = if (sizeCol >= 0 && !cursor.isNull(sizeCol)) cursor.getLong(sizeCol) else -1L
                        val path = if (current.path.isEmpty()) name else current.path + "/" + name

                        if (mime == DocumentsContract.Document.MIME_TYPE_DIR) {
                            foldersSeen++
                            stack.add(Pending(childId, path))
                            continue
                        }

                        filesSeen++
                        val docUri = DocumentsContract.buildDocumentUriUsingTree(treeUri, childId)

                        if (name.contains(query, ignoreCase = true)) {
                            hits += "NAME: $path"
                            if (hits.size >= MAX_MATCHES) break
                        }

                        if (isTextLike(name, mime) && (size < 0 || size <= MAX_TEXT_BYTES)) {
                            searchTextFile(context, docUri, path, query, hits)
                        }
                    }
                }
            } catch (_: SecurityException) {
                return "Folder permission was lost. Choose the folder again."
            } catch (_: Throwable) {
                // One unreadable provider node must not stop the rest of the search.
            }
        }

        val result = buildString {
            append("PHONE FILE SEARCH\n")
            append("Query: ").append(query).append('\n')
            append("Folders checked: ").append(foldersSeen).append('\n')
            append("Files checked: ").append(filesSeen).append('\n')
            append("Matches: ").append(hits.size).append("\n\n")
            if (hits.isEmpty()) {
                append("No matches found.")
            } else {
                hits.forEachIndexed { index, hit ->
                    append(index + 1).append(". ").append(hit).append('\n')
                }
                if (hits.size >= MAX_MATCHES) append("\nStopped after $MAX_MATCHES matches.")
            }
        }

        LocalBridgeSender.send(
            DeviceEvent(
                source = "file_search",
                packageName = context.packageName,
                title = query,
                text = result
            )
        )

        return result
    }

    private fun searchTextFile(
        context: Context,
        uri: Uri,
        path: String,
        query: String,
        hits: MutableList<String>
    ) {
        try {
            context.contentResolver.openInputStream(uri)?.bufferedReader()?.use { reader ->
                var lineNumber = 0
                while (true) {
                    val line = reader.readLine() ?: break
                    lineNumber++
                    if (line.contains(query, ignoreCase = true)) {
                        val excerpt = line.trim().replace(Regex("\\s+"), " ").take(500)
                        hits += "TEXT: $path:$lineNumber — $excerpt"
                        if (hits.size >= MAX_MATCHES) return
                    }
                }
            }
        } catch (_: Throwable) {
            // Skip files that are not readable as text.
        }
    }

    private fun isTextLike(name: String, mime: String): Boolean {
        if (mime.startsWith("text/")) return true
        val lower = name.lowercase()
        return lower.endsWith(".txt") ||
            lower.endsWith(".md") ||
            lower.endsWith(".html") ||
            lower.endsWith(".htm") ||
            lower.endsWith(".csv") ||
            lower.endsWith(".json") ||
            lower.endsWith(".xml") ||
            lower.endsWith(".log") ||
            lower.endsWith(".sh") ||
            lower.endsWith(".py") ||
            lower.endsWith(".kt") ||
            lower.endsWith(".java")
    }
}
