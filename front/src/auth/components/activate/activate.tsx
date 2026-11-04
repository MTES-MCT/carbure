import { LoaderLine } from "common/components/icon"
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import { Text } from "common/components/text"
import { useActivate } from "./activate.hooks"

export const Activate = () => {
  const { success, title, loading, message, action } = useActivate()

  return (
    <Container success={success} title={title}>
      <Content>
        <Section>
          {loading && <LoaderLine style={{ fontSize: "48px" }} />}
          {message && <Text>{message}</Text>}
        </Section>
        {action && <FooterAuth asideX>{action}</FooterAuth>}
      </Content>
    </Container>
  )
}
