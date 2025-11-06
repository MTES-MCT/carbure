import { ReactNode } from "react"
import React from "react"
import { Notice } from "../../src/common/components/notice"
import { Text } from "../../src/common/components/text"

const StoryDescription = ({ description }: { description: ReactNode }) => {
  if (!description) return null
  return (
    <Notice
      title="Story description"
      style={{
        position: "absolute",
        bottom: "8px",
        right: "8px",
        maxWidth: "500px",
        border: "2px dashed var(--border-default-grey)",
        zIndex: 1000,
      }}
      isClosable
    >
      <Text size="sm">{description}</Text>
    </Notice>
  )
}

export default StoryDescription
