import React, { useState } from 'react'
import {
  Box,
  Container,
  VStack,
  Heading,
  Input,
  Button,
  Text,
  useToast,
  Textarea,
  HStack,
  Divider,
  Card,
  CardBody,
} from '@chakra-ui/react'
import axios from 'axios'

function App() {
  const [file, setFile] = useState(null)
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setLoading(true)
      const response = await axios.post('/api/upload', formData)
      toast({
        title: 'Success',
        description: response.data.message,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Upload failed',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleChat = async () => {
    if (!query.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a question',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      setLoading(true)
      const response = await axios.post('/api/chat', { query })
      setAnswer(response.data.answer)
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Chat failed',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSummarize = async () => {
    try {
      setLoading(true)
      const response = await axios.post('/api/summarize')
      setSummary(response.data.summary)
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Summarization failed',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading textAlign="center">PDF Chat Assistant</Heading>
        
        <Card>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Heading size="md">Upload PDF</Heading>
              <Input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={loading}
              />
              {file && <Text>Selected file: {file.name}</Text>}
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Heading size="md">Chat with PDF</Heading>
              <Textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about the PDF..."
                disabled={loading || !file}
              />
              <HStack>
                <Button
                  colorScheme="blue"
                  onClick={handleChat}
                  isLoading={loading}
                  disabled={!file}
                  flex={1}
                >
                  Ask Question
                </Button>
                <Button
                  colorScheme="green"
                  onClick={handleSummarize}
                  isLoading={loading}
                  disabled={!file}
                  flex={1}
                >
                  Summarize PDF
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {(answer || summary) && (
          <Card>
            <CardBody>
              <VStack spacing={4} align="stretch">
                {answer && (
                  <Box>
                    <Heading size="md" mb={2}>Answer</Heading>
                    <Text whiteSpace="pre-wrap">{answer}</Text>
                  </Box>
                )}
                {answer && summary && <Divider />}
                {summary && (
                  <Box>
                    <Heading size="md" mb={2}>Summary</Heading>
                    <Text whiteSpace="pre-wrap">{summary}</Text>
                  </Box>
                )}
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Container>
  )
}

export default App