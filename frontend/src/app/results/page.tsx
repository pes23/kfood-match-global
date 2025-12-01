import {
  Box,
  Button,
  Container,
  Heading,
  Spinner,
  Text,
  VStack,
  Alert,
  AlertIcon,
  HStack,
} from "@chakra-ui/react";
import Link from "next/link";
import { Suspense } from "react";
import ResultsContent from "./results-content";

type ResultsPageProps = {
  searchParams: { food?: string };
};

export default function ResultsPageWrapper({ searchParams }: ResultsPageProps) {
  return (
    <Suspense
      fallback={
        <Container maxW="container.lg" py={16}>
          <VStack spacing={6} align="center">
            <Spinner />
            <Text>추천 결과를 불러오는 중입니다...</Text>
            <Text>Loading recommendation results...</Text>
          </VStack>
        </Container>
      }
    >
      <ResultsContent searchParams={searchParams} />
    </Suspense>
  );
}
